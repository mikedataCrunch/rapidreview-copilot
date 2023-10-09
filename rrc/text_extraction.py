"""This module contains the scripts used for extracting text data from
reference managers, pdfs, and other common sources for review.
"""

# import libraries and set up depedencies 
import pandas as pd
from glob import glob
from pyzotero import zotero
import json

# pdf extractor
class PDFExtractor():
    """This class instantiates the PDF Extractor class."""
    def __init__(self, src_dir, extractor, metadata_path=None, paths_col=None,):
        self.src_dir = src_dir
        self.extractor = extractor
        self.metadata_path = metadata_path
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
            pass
            # extraction specific to that package
        elif extradctor=="other name":
        
        
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
class ZoteroAPIMetaExtractor():
    """This class instantiates the reference manager extractor class."""
    def __init__(self, path = None, filetype =None):
        self.path = path
        self.filetype = filetype

    def extract(self, library_id, library_type, api_key, collection_key=None):
        """
        library_id     --> library id as XXXXX 'www.zotero.org/groups/XXXXX/[library_name]'
        library_type   --> as 'group' for shared group library and 'user' for own Zotero library
        api_key        --> personal Zotero API key
        collection_key --> for specifc collection only
        filetype       --> extract metadata as [json, csv]
        """
        # Initialize the Zotero library
        zot = zotero.Zotero(library_id, library_type, api_key)

        # Create an empty list to store item data
        zotero_metadata_list = []
        
        # retrieve items in specifc collection
        if collection_key:  
            try:
                # Retrieve all items within the specific collection
                items = zot.collection_items(collection_key)
            except:
                return "Response: Collection not found"  
        # retrieve items in all collection 
        else:
            # retrieve all items
            items = zot.everything(zot.items())
        
        # add items into list
        try:    
            for item in items:
                if 'collections' in item['data'].keys():
                    zotero_metadata_list.append(item['data'])
        except:
            return "Response: No item in collections1"
        
        # filetype choice 
        if self.filetype.lower() == "json":
            with open('ZoteroMetadata.json', 'w') as json_file:
                json.dump(zotero_metadata_list , json_file)
            return
        elif self.filetype.lower() == "csv":
            pd.DataFrame.from_dict(zotero_metadata_list).to_csv("ZoteroMetadata.csv", index = False)
            return 
        else:
            return 'File type not available.'
        

# running from terminal
if __name__ == "__main__":
    pass
    



