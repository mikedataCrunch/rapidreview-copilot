## Tasks
## 1. Add necessary imports and set ups (check if extra set up is needed for FAISS to work)
## 2. Debug script e.g., ensure variable names consistency, ensure the script runs as expected
## 3. Add docstring to class and methods, see guide: https://www.programiz.com/python-programming/docstrings
## 4. Demo a session in the tutorials notebook (NOTE: PDF extractor output json keys must be consistent with article_id and extracted_text keys, current: "article id" and "extracted id")

from tqdm import tqdm
from glob import glob
import os
from typing import Optional

import json

# for review
from transformers import AutoTokenizer
from haystack.pipelines import Pipeline
from haystack.nodes import  PromptNode, PromptTemplate, AnswerParser
from haystack.schema import Document

# document store
from haystack.document_stores import FAISSDocumentStore

# retriever
from haystack.nodes import DensePassageRetriever

class RapidReviewSession():
    """
    RapidReviewSession is a customizable node designed for easy integration into NLP pipelines, 
    leveraging the capabilities of large language models for efficient question-answering.

    The class uses PromptNode from Haystack and FAISSDocumentStore for question-answering with the 
    aid of prompts. Prompts are introduced to PromptNode through PromptTemplate, with an emphasis on 
    task-specific templates for improved results.

    To optimize performance, it is recommended to use task-specific PromptTemplates and pass variables 
    like documents or questions to the node. The class seamlessly combines inputs into prompts, making 
    it suitable for various NLP tasks.

    Due to the token length limitations of different pretrained models, chunking will be done based 
    on user input. These chunks will be retrieved by the Retriever as Documents and passed to the node.
    """

    def __init__(
        self, 
        src_dir: str, 
        ret_models: tuple, 
        ret_top_k: int, 
        qa_model: str, 
        max_ans_length: Optional[int] = 100,
        min_context_size: Optional[int] = 200, 
        seq_length_buffer: Optional[int] = 50
    ):
        """ 
        Creates a RapidReview instance. 
        
        :param src_dir: The name of the source directory where JSON files are being stored.
        :param ret_models: Tuple of retriever models. First element to be the Query Embedding model, 
            second element to be the Context Embedding model
        :param ret_top_k: Top k chunks retrieved from document store based on query.
        :param qa_model: The name of the model to use or an instance of the PromptModel.
        :param max_ans_length: he maximum number of tokens the generated text output can have.
            If not set, default 100
        :param min_context_size: The minimum chunk size that user wish to input. 
            If not set, default 200
        :param seq_length_buffer: The number of token length to buffer for difference in chunking tokenizer and generator tokenizer
            If not set, default 50
        """
        # session text sources
        self.src_dir = src_dir

        # retriever models 
        self.query_embedding_model = ret_models[0]
        self.context_embedding_model = ret_models[1]
        self.ret_top_k = ret_top_k
        self.ret_tokenizer = AutoTokenizer.from_pretrained(
            self.context_embedding_model
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
    
    # check for token length
    def _get_context_size(
        self,
        prompt: str, 
        query: str
    ):
        """
        Checking if allocated variables exceeds model max token length 
        
        :param prompt: The name of hard coded prompts in prompt_template module: https://docs.haystack.deepset.ai/docs/prompt_node#prompttemplate-structure:~:text=List%20of%20legacy,translation%0ATranslates%20documents.
            Else, user can specify their own prompts.
        :param query: Question to be answered by the generator model
        :return None
        """
        self.query_length = self.qa_tokenizer(query, return_tensors="pt")
        self.prompt_length = self.qa_tokenizer(prompt, return_tensors="pt")
        self.context_size = (
            self.qa_max_length
            - len(self.query_length["input_ids"]) 
            - len(self.prompt_length["input_ids"])
            - self.seq_length_buffer 
            - self.max_ans_length
        )
        if self.context_size < self.min_context_size:
            raise ValueError("Prompt + Query is too long.")
        pass
    # check for chunk size exceeding the model max seq length
    def _get_chunk_size(self):
        self.chunk_size = self.context_size // self.ret_top_k
        if self.chunk_size > self.ret_max_length:
            RuntimeError(
                f"Chunk size ({self.chunk_size}) is longer than Retriever MAX SEQ LENGTH")
        elif self.chunk_size > self.qa_max_length:
            RuntimeError(
                f"Chunk size ({self.chunk_size}) is longer than QA model MAX SEQ LENGTH")
        pass
    # chunking articles (in certain format) based on chunk size 
    def _chunk_articles(self, params, fmt="json"):
        """ """
        documents = []
        # Obtain chosen article
        chosen_article_id = params["Retriever"]["filters"]['article_id']
        doc_paths = glob(os.path.join(self.src_dir, f'*.{fmt}'))
        for path in tqdm(doc_paths):
            with open(path, 'r') as file:
                data = json.load(file)
                article_id = data.get("article_id")
                if (article_id == chosen_article_id):
                    extracted_context = data.get("extracted_text")
            
        # NOTE: QA tokenizer is used to get the correct seq lengths
        tokenized_context = self.ret_tokenizer(
            extracted_context, return_tensors="pt").input_ids
        counter = 0
        for tokenized_list in tokenized_context:
            for start_index in range(
                    0, len(tokenized_list), self.chunk_size):
                # handles contexts with length not divisible by chunk_size
                if start_index + self.chunk_size >= len(tokenized_list):
                    tokenized_chunk = tokenized_list[start_index:]
                else:
                    tokenized_chunk = tokenized_list[start_index: start_index + self.chunk_size]
                chunk_text = self.ret_tokenizer.decode(tokenized_chunk)
                meta = data.copy()
                meta["chunk_id"] = f"{article_id}_{counter}"
                # using a linux path to file, extract file name e.g., some_title.pdf
                meta["filename"] = os.path.basename(
                    os.path.realpath(path)
                ) # verify if this works in windows paths
            
                chunk_data = Document(content=chunk_text, meta=meta)
                documents.append(chunk_data)
                counter += 1

        return documents
    
    def _init_document_store(
        self,
        params,
        index_path="./doc_store_index.faiss", 
        config_path="./doc_store_config.json"
    ):
        """ 
        Creates a FAISS document store to store all chunks from articles as Documents. 
        Dense Passage Retriever (DPR) is used to produce embeddings for Documents 
        
        :param index_path: Path to save the index.
        :param config_path: Path to save the configuration file. 
                This is the JSON file that contains all the parameters to initialize the DocumentStore.
        :return: None
        """
        
        self.index_path = index_path
        self.config_path = config_path
        
        # Run this if document store not initialize
        if not hasattr(self, 'document_store') or self.document_store is None:
            # Load document store 
            self.document_store = FAISSDocumentStore(
                sql_url="sqlite:///faiss_document_store.db",)
        else: 
            self.document_store = FAISSDocumentStore.load(
                index_path=self.index_path, 
                config_path=self.config_path)
        
        # Writing and saving embeddings to document store
        documents = self._chunk_articles(params)
        # Set up retriever
        self.retriever = DensePassageRetriever(
            document_store=self.document_store,
            query_embedding_model=self.query_embedding_model,
            passage_embedding_model=self.context_embedding_model,
            embed_title=True)
        # Delete document store before writing
        # Vectors changed when token length changes, delete the file to flush 
        self.document_store.delete_documents()
        self.document_store.write_documents(documents)
        # Update embeddings
        self.document_store.update_embeddings(retriever=self.retriever)
        # Save after updating embeddings
        self.document_store.save(index_path=self.index_path, config_path=self.config_path)
        pass
    
    def _reset_document_store(self):
        """
        Flush all existing documents, followed by saving document store. 
        To be called after obtaining answers from query
        """
        self.document_store.delete_documents()
        self.document_store.save(index_path=self.index_path, config_path=self.config_path)

    # Obtain document chunk ids
    def get_document_chunks_ids(
        self,
        prompt: str, 
        query: str,
        params
    ):
        """
        Obtain document and chunk ids.
         :param prompt: The name of hard coded prompts in prompt_template module: https://docs.haystack.deepset.ai/docs/prompt_node#prompttemplate-structure:~:text=List%20of%20legacy,translation%0ATranslates%20documents.
            Else, user can specify their own prompts.
        :param query: Question to be answered by the generator model.
        :return: nested list of document and chunk ids.
        """
        self._get_context_size(prompt, query)
        self._get_chunk_size()
        documents = self._chunk_articles(params)
        chunk_ids = []
        for document in documents:
            # document.id may not be required
            chunk_ids.append([document.id, document.meta['chunk_id']])
        return chunk_ids
    def run_query(
        self, 
        prompt: str, 
        query: str, 
        params: dict
        ):
        """ 
        Generate answers with generator model given prompt, query and params. 
        
        :param prompt: The name of hard coded prompts in prompt_template module: https://docs.haystack.deepset.ai/docs/prompt_node#prompttemplate-structure:~:text=List%20of%20legacy,translation%0ATranslates%20documents.
            Else, user can specify their own prompts.
        :param query: Question to be answered by the generator model.
        :param params: Dictionary of top k and article id. 
        :return [Dictionary] of query and answers.
        """
        # initialize chunking dependencies
        self._get_context_size(prompt, query)
        self.ret_top_k = params.get("Retriever").get("top_k")
        if not self.ret_top_k:
            raise RuntimeError("Retriever top_k must be specified in params.")
            
        self._get_chunk_size()
        
        # Init or Load doc store 
        self._init_document_store(params)
        
        # Init PromptTemplate
        prompt_template = PromptTemplate(
            prompt=prompt,
            output_parser=AnswerParser(),
        )
        
        # Init PromptNode, provide answer limit
        prompt_node = PromptNode(
            self.qa_model,
            default_prompt_template=prompt_template,
            max_length = self.max_ans_length
        )
        
        # Init Pipeline
        pipe = Pipeline()
        pipe.add_node(component=self.retriever,
                      name="Retriever", inputs=["Query"])
        pipe.add_node(component=prompt_node,
                      name="PromptNode", inputs=["Retriever"])
        output = pipe.run(query=query, params=params)
        # resets document store
        self._reset_document_store()
        return dict(zip(output["query"], output["answers"]))
