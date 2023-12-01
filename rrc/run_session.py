## Tasks
## 1. Add necessary imports and set ups (check if extra set up is needed for FAISS to work)
## 2. Debug script e.g., ensure variable names consistency, ensure the script runs as expected
## 3. Add docstring to class and methods, see guide: https://www.programiz.com/python-programming/docstrings
## 4. Demo a session in the tutorials notebook (NOTE: PDF extractor output json keys must be consistent with article_id and extracted_text keys, current: "article id" and "extracted id")

from tqdm import tqdm
from glob import glob
import os


class RapidReviewSession():
    """ """

    def __init__(src_dir, ret_models, qa_model, max_ans_length,
                 min_context_size=200, seq_length_buffer=50,):
        """ """
        # session text sources
        self.src_dir = src_dir

        # retriever models
        self.context_embedding_model = ret_models[0]
        self.query_embedding_model = ret_models[1]
        self.ret_top_k = ret_top_k
        self.ret_tokenizer = AutoTokenizer.from_pretrained(
            self.context_embedding
        )

        # generative model
        self.qa_model = qa_model
        self.qa_tokenizer = AutoTokenizer.from_pretrained(
            self.qa_model
        )

        # other session parameters
        self.ret_max_length = self.ret_tokenizer.model_max_length
        self.qa_max_length = self.qa_tokenizer.model_max_length
        self.max_ans_length = max_ans_length
        self.seq_length_buffer = seq_length_buffer
        self.min_context_size = min_context_size

        print(f"Retriever MAX SEQ LENGTH: {self.ret_max_length}")
        print(f"QA model MAX SEQ LENGTH (Input limit): {self.qa_max_length}")

    def _get_context_size(self, prompt, query):
        self.query_length = self.qa_tokenizer(query, return_tensors="pt")
        self.prompt_length = self.qa_tokenizer(prompt, return_tensors="pt")
        self.context_size = (
            self.qa_max_length
            - self.query_length - self.prompt_length
            - self.seq_length_buffer - self.max_ans_length
        )
        if self.context_size < min_context_size:
            raise ValueError("Prompt + Query is too long.")
        pass

    def _get_chunk_size(self, retriever_top_k):
        self.chunk_size = self.context_size // retriever_top_k
        if self.chunk_size > self.ret_max_length:
            RuntimeError(
                f"Chunk size ({self.chunk_size}) is longer than Retriever MAX SEQ LENGTH")
        elif self.chunk_size > self.qa_max_length:
            RuntimeError(
                f"Chunk size ({self.chunk_size}) is longer than QA model MAX SEQ LENGTH")
        pass

    def _chunk_articles(self, fmt="json"):
        """ """
        documents = []
        doc_paths = glob(os.path.join(self.src_dir, f'*.{fmt}'))
        for path in tqdm(doc_paths):
            with open(path, 'r') as file:
                data = json.load(file)
                article_id = data.get("article_id")  # snake case
                extracted_context = data.get("extracted_text")  # snake case

            # NOTE: QA tokenizer is used to get the correct seq lengths
            tokenized_context = self.qd_tokenizer(
                extracted_context, return_tensors="pt").input_ids

            counter = 0
            for start_index in range(
                    0, len(tokenized_context, self.chunk_size)):

                # handles contexts with length not divisible by chunk_size
                if start_index + self._chunk_size >= len(tokenized_context)
                tokenized_chunk = tokenized_context[start_index:]
                else:
                    tokenized_chunk = tokenized_context[start_index: start_index + self._chunk_size]

                chunk_text = self.ret_tokenizer.decode(tokenized_chunk)
                meta = data.copy()
                meta["chunk_id"] = f"{article_id}_{counter}"

                # using a linux path to file, extract file name e.g., some_title.pdf
                meta["filename"] = os.path.basename(
                    os.path.realpath(path)
                ) # verify if this works in windows paths
                
                
                chunk_data = Document("content"=chunk_text, "meta"=meta,)
                documents.append(chunk_data)
                counter += 1

                return documents

    def _create_document_store(self, index_path="./doc_store_index.faiss"):
        """ """
        documents = self._chunk_articles()
        # I changed to FAISS: Do the set up needed to get this to work
        self.document_store = FAISSDocumentStore(
            faiss_index_factory_str="Flat")
        self.document_store.save(index_path=path)
        self.document_store.write_documents(documents)
        pass

    def _init_document_store(self,):
        """ """
        self.retriever = DensePassageRetriever(
            document_store=self.document_store,
            query_embedding_model=self.query_embedding_model,
            passage_embedding_model=self.context_embedding_model,
            embed_title=True)
        self.document_store.update_embeddings(retriever=self.retreiver)
        pass

    def run_query(self, prompt, query, article_id, params):
        """ """
        # initialize chunking dependencies
        self._get_context_size(prompt, query)
        retriever_top_k = params.get("retriever").get("top_k")
        if not retreiver_top_k:
            raise RuntimeError("Retriever top_k must be specified in params.")
            
        self._get_chunk_size(retriever_top_k)
        
        # trigger self._chunk_articles, and init doc store
        self._create_document_store()
        
        # trigger encoding into doc store
        self._init_document_store()

        prompt_template = PromptTemplate(
            prompt=prompt,
            output_parser=AnswerParser(),
        )

        prompt_node = PromptNode(
            self.qa_model,
            default_prompt_template=prompt_template,
        )
        pipe = Pipeline()
        pipe.add_node(component=self.retreiver,
                      name="retriever", inputs=["Query"])
        pipe.add_node(component=prompt_node,
                      name="prompt_node", inputs=["retriever"])
        output = pipe.run(query=query, params=params)
        return dict(zip(output["query"], output["answers"]))
