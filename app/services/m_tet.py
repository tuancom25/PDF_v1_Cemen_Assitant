import os 
from pathlib import Path
document_path = Path("data/processed/documents")
list_dict_document = {}
documents = []
documents = document_path.glob("*")
#for pdf_file in document_path.glob("*"):
for pdf_file in documents:
            print(f"Found file __ : {pdf_file}")
            #document_name = pdf_file.stem
            #documents.append(document_name)
            #list_dict_document[document_name] = pdf_file