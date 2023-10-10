"""This module contains the scripts used for extracting text data from
reference managers, pdfs, and other common sources for review.
"""

# import libraries and set up depedencies 
from glob import glob
import numpy as np
import pandas as pd
import os

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
    def __init__(self, src_dir, paths_col=None, metadata=None):
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
    
    def extract(self, extractor, path=None):
        """Extract PDF text from pdf filepath and returns extracted text in a json structure"""
        
        # concat src_dir and relative path
        full_path = os.path.join(self.src_dir, path)

        try:
            # Check if the path exists
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"The file at path '{full_path}' does not exist.")
            # include the choice of python pdf extract package to use
            if extractor=='pdfplumber':
                # List to store extracted text as dictionaries
                extracted_text_list = []
                # Extract the text
                with pdfplumber.open(full_path) as pdf:
                    for page_num, page in enumerate(pdf.pages, start=1):
                        # Get the bounding boxes of the tables on the page.
                        bboxes = [
                            table.bbox
                            for table in page.find_tables(
                                table_settings={
                                    "vertical_strategy": "explicit",
                                    "horizontal_strategy": "explicit",
                                    "explicit_vertical_lines": page.curves + page.edges,
                                    "explicit_horizontal_lines": page.curves + page.edges,
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

                        # Extract text from the page
                        extracted_text = page.filter(not_within_bboxes).extract_text()

                        # Create a dictionary with "page" and "extracted text" keys
                        page_dict = {"page": page_num, "extracted text": extracted_text}
                        
                        # Append the dictionary to the list
                        extracted_text_list.append(page_dict)

                    # Return the list of dictionaries
                    return extracted_text_list
                
            elif extractor == 'PdfReader':
                # Creating a pdf reader object
                reader = PdfReader(full_path)
                # List to store extracted text as dictionaries
                extracted_text_list = []

                # Loop through every page
                for page_num in range(reader.numPages):
                    # Get a specific page
                    page = reader.getPage(page_num)

                    # Extract text from the page
                    page_text = page.extract_text()

                    # Create a dictionary with "page" and "extracted text" keys
                    page_dict = {"page": page_num + 1, "extracted text": page_text}

                    # Append the dictionary to the list
                    extracted_text_list.append(page_dict)

                # Return the list of dictionaries
                return extracted_text_list

        except FileNotFoundError as e:
            return [{"error": str(e)}]
        except Exception as e:
            return [{"error": str(e)}]

        
    def mass_extract(self, extractor=None, include_meta=False, dest_dir=None):
        """Extract PDF text from all pdfs self.paths and store the output in a specified directory"""
        
        # If dest_dir is not specified, use a temporary directory
        if extractor is None and dest_dir is None:
            dest_dir = tempfile.mkdtemp(dir='.')
        
        elif extractor == 'pdfplumber': 
            for path in self.paths:
                if path.endswith(".pdf"):
                    extracted_data = self.extract(extractor='pdfplumber', path=path)
                    pdf_file_name = os.path.basename(path)
                    json_file_name = os.path.splitext(pdf_file_name)[0] + '.json'
                    json_file_path = os.path.join(dest_dir, json_file_name)
                    # Write extracted data to the JSON file
                    with open(json_file_path, 'w') as json_file:
                        json.dump(extracted_data, json_file, indent=4)
            return dest_dir
        
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
            return dest_dir
        
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
        pass
        #yield chunk
    
    def persist(self, dest_dir):
        """Persists all files in the temporary directory into a dest_dir"""
        pass
    
    pass

# reference manager extractor
class ZoteroAPIMetaExtractor():
    """This class instantiates the reference manager extractor class."""
    def __init__(self, path, filetype):
        self.path = path
        self.filetype = filetype
    pass


# running from terminal
if __name__ == "__main__":
    pass
    



