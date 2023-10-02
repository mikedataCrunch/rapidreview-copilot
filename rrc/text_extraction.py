"""This module contains the scripts used for extracting text data from
reference managers, pdfs, and other common sources for review.
"""

# import libraries and set up depedencies 
from glob import glob


# pdf extractor
class PDFExtractor(src_dir, extractor, metadata_path=None, paths_col=None,):
    """This class instantiates the PDF Extractor class."""
    def __init__(src_dir, metadta):
        self.src_dir = src_dir
        self.metadata_path = metadata
        self.paths_col = paths_col
        self.metadata = None
        self.paths = None
    
    def _get_paths(self):
        if self.paths_col:
            self.metadata = pd.read_csv(self.metadata)
            self.paths = self.metadata[self.paths_col].tolist()
        else:
            self.paths = glob(os.path.join(src_dir, '*'))
    
    def extract(self, index=None, path=None):
        """Extract PDF text from pdf filepath and returns extracted text in a json structure"""
        # concat src_dir and relative path
        # include the choice of python pdf extract package to use
        if extractor=='some_name':
            # extraction specific to that package
        elif extradctor=:
        
        
        # use concat path as input to pdf extractor
        
        pass
        
    def mass_extract(self, include_meta=False):
        """Extract PDF text from all pdfs self.paths and store the output in a temporary directory"""
        # run self.extract iteratively and saves them in a temporary directory as json files
        # {'path': <extracted_text>} ---> sample structure
        
        # if include_meta is true, append metadata using column name and value as key:value pairs
        if self.metadata and include_meta:
            pass
        
        pass
    
    def load_sample(self, paths=None, sample_size=3):
        if paths:
            sample_texts = None # load json from temporary directory into memory
        else:
            sample_texts = None # randomly choose sample_size from the temporary directory   
        return sample_texts
    
    def extract_chunks(self, chunk_size=5):
        # generator: chuck paths into chunk size and return into memory
        
        yield chunk
    
    def persist(self, dest_dir):
        """Persists all files in the temporary directory into a dest_dir"""
        pass
    
    pass

# reference manager extractor
class ZoteroAPIMetaExtractor(path, filetype):
    """This class instantiates the reference manager extractor class."""
    
    pass


# running from terminal
if __name__ == "__main__":
    pass
    



