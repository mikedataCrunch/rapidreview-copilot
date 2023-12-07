"""This module contains the scripts used for extracting text data from
reference managers, pdfs, and other common sources for review.
"""

# import libraries and set up depedencies 
import pandas as pd
from glob import glob
from pyzotero import zotero
import numpy as np
import pandas as pd
import os
import uuid
import re

# extract text from pdfs
import pdfplumber
from PyPDF2 import PdfReader

# temporary file
import tempfile

# json
import json

# pdf extractor
class PDFExtractor():
    """This class instantiates the PDF Extractor class."""
    def __init__(
        self, 
        src_dir : str, 
        paths_col=None, 
        metadata=None
    ):
        # Check if src_dir exists
        if not os.path.exists(src_dir):
            raise ValueError(f"The specified source directory '{src_dir}' does not exist.")
        """
        Creates a PDFExtractor instance.

        :param src_dir: The name of the source directory where PDF files are being stored.
        :param extractor: Extractor must be either "pdfplumber" or "PdfReader".
        :param paths_col: 
        :param metadata: 
        
        """
        self.src_dir = src_dir
        self.bboxes = []
        self.paths_col = paths_col
        self.metadata = metadata
        self._get_paths(src_dir)
    
    def _get_paths(self, src_dir):
        if self.paths_col:
            self.metadata   = pd.read_csv(self.metadata)    
            self.paths = self.metadata[self.paths_col].tolist()
        else:
            self.paths = glob(os.path.join(src_dir, '*'))
        return self.paths
    
    def generate_article_id(self):
        # Generate a UUID-based article ID
        return str(uuid.uuid4())

    def extract(self, extractor, path=None):
        """Extract PDF text from pdf filepath and returns extracted text in a json structure"""
        
        # concat src_dir and relative path
        #full_path = os.path.join(self.src_dir, path)
        #print(full_path)
        try:
            # Check if the path exists
            if not os.path.exists(path):
                raise FileNotFoundError(f"The file at path '{path}' does not exist.")
            # include the choice of python pdf extract package to use

            # Generate unique article id
            article_id = self.generate_article_id()
            extracted_text = ""
            
            if extractor=='pdfplumber':
                # Extract the text
                with pdfplumber.open(path) as pdf:
                    for page in pdf.pages:
                        # Get the bounding boxes of the tables on the page.
                        bboxes = [
                            table.bbox
                            for table in page.find_tables(
                                table_settings={
                                    "vertical_strategy": "lines",
                                    "horizontal_strategy": "lines",
                                }
                            )
                        ]

                        # Function to check if an object is within any bounding box
                        def not_within_bboxes(obj):
                            def obj_in_bbox(_bbox):
                                v_mid = (obj["top"] + obj["bottom"]) / 2
                                h_mid = (obj["x0"] + obj["x1"]) / 2
                                x0, top, x1, bottom = _bbox
                                return (h_mid >= x0) and (h_mid < x1) and (v_mid >= top) and (v_mid < bottom)

                            return not any(obj_in_bbox(__bbox) for __bbox in bboxes)
                        
                         # Extract text from the page and concatenate it
                        page_text = page.filter(not_within_bboxes).extract_text()
                        extracted_text += page_text

                    # Create a dictionary with article id and "extracted text" keys
                    output = {"article_id": article_id, "extracted_text": extracted_text}

                    # Return the list of dictionaries
                    return output
                
            elif extractor == 'PdfReader':
                # Creating a pdf reader object
                reader = PdfReader(path)

                # Loop through every page
                for page_num in range(len(reader.pages)):
                    
                    # Get a specific page
                    page = reader.pages[page_num]

                    # Extract text from the page
                    extracted_text += re.sub("[\t\n\x0b\r\f]", ' ', page.extract_text()) + " "

                # Create a dictionary with "page" and "extracted text" keys
                output = {"article_id": article_id, "extracted_text": extracted_text}

                # Return the list of dictionaries
                return output

        except FileNotFoundError as e:
            return [{"error": str(e)}]
        except Exception as e:
            return [{"error": str(e)}]

        
    def mass_extract(self, extractor, include_meta=False, dest_dir=None):
        """Extract PDF text from all pdfs self.paths and store the output in a specified directory"""
        filename_list = []
        self.dest_dir = dest_dir
        # If dest_dir is not specified, use a temporary directory
        if dest_dir is None:
            dest_dir = tempfile.mkdtemp(dir='.')
        
        if extractor == 'pdfplumber': 
            for path in self.paths:
                if path.endswith(".pdf"):
                    extracted_data = self.extract(extractor='pdfplumber', path=path)
                    pdf_file_name = os.path.basename(path)
                    json_file_name = os.path.splitext(pdf_file_name)[0] + '.json'
                    json_file_path = os.path.join(dest_dir, json_file_name)
                    # Write extracted data to the JSON file
                    with open(json_file_path, 'w') as json_file:
                        json.dump(extracted_data, json_file, indent=4)
                        filename_list.append(json_file_name)
            return filename_list
        
        elif extractor == 'PdfReader': 
            for path in self.paths:
                if path.endswith(".pdf"):
                    extracted_data = self.extract(extractor='PdfReader', path=path)
                    pdf_file_name = os.path.basename(path)
                    json_file_name = os.path.splitext(pdf_file_name)[0] + '.json'
                    json_file_path = os.path.join(dest_dir, json_file_name)
                    # Write extracted data to the JSON file
                    with open(json_file_path, 'w') as json_file:
                        json.dump(extracted_data, json_file, indent=4)
                        filename_list.append(json_file_name)
            return filename_list
        
        # run self.extract iteratively and saves them in a temporary directory as json files
        # {'path': <extracted_text>} ---> sample structure
        
        # if include_meta is true, append metadata using column name and value as key:value pairs
        if self.metadata and include_meta:
            pass    
        
        pass
    def get_extracted(self):
        if self.dest_dir is None:
            raise RuntimeError("mass_extract() must be called before get_extracted()")
        return self.dest_dir
        
    
    def load_sample(self, paths=None, sample_size=3):
        if paths:
            sample_texts = None # load json from temporary directory into memory
        else:
            sample_texts = None # randomly choose sample_size from the temporary directory   
        return sample_texts
    
    def extract_chunks(self, chunk_size=5):
        # generator: chuck paths into chunk size and return into memory
        pass
        #yield chunk
    
    def persist(self, dest_dir):
        """Persists all files in the temporary directory into a dest_dir"""
        pass
    
    pass

# reference manager extractor
class ZoteroAPIMetaExtractor():
    """This class instantiates the reference manager extractor class."""
    def __init__(self, filetype):
        self.filetype = filetype
    pass

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
        
        # Create the folder if it doesn't exist
        folder_name = 'ZoteroMeta'
        os.makedirs(folder_name, exist_ok=True)
        
        # filetype choice 
        if self.filetype.lower() == "json":
            json_file_path = os.path.join(folder_name, 'ZoteroMetadata.json')
            with open(json_file_path, 'w') as json_file:
                json.dump(zotero_metadata_list , json_file)
            return f"JSON file created: {json_file_path}"
        elif self.filetype.lower() == "csv":
            csv_file_path = os.path.join(folder_name, 'ZoteroMeta.csv')
            pd.DataFrame.from_dict(zotero_metadata_list).to_csv(csv_file_path, index = False)
            return f"CSV file created: {csv_file_path}"
        else:
            return 'File type not available.'
        

# running from terminal
if __name__ == "__main__":
    pass
    



