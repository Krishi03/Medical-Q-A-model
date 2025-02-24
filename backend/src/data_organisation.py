import os
import json
import shutil
from typing import Dict, List

def setup_data_directories():
    """Create necessary directories for data organization."""
    dirs = [
        'data/medical_documents/clinical_guidelines',
        'data/medical_documents/patient_education',
        'data/medical_documents/web_content',
        'data/processed',
        'data/vector_store'
    ]
    
    for dir_path in dirs:
        try:
            full_path = f'c:/Users/krish/medical/backend/{dir_path}'
            if not os.path.exists(full_path):
                os.makedirs(full_path)
        except FileExistsError:
            
            pass
        except Exception as e:
            print(f"Error creating directory {dir_path}: {str(e)}")

def scan_documents() -> List[Dict]:
    """Scan medical documents and extract metadata."""
    documents = []
    base_path = os.path.normpath('c:/Users/krish/medical/backend/data/medical_documents')
    

    for folder in ['clinical_guidelines', 'patient_education', 'web_content']:
        folder_path = os.path.normpath(os.path.join(base_path, folder))
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            try:
                for filename in os.listdir(folder_path):
                    if filename.endswith('.txt'):
                        file_path = os.path.join(folder_path, filename)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            
                            lines = content.split('\n')
                            metadata = {}
                            for line in lines[:5]:
                                if ': ' in line:
                                    key, value = line.split(': ', 1)
                                    metadata[key.lower()] = value
                            
                            documents.append({
                                'file_path': file_path,
                                'content': content,
                                'source_type': folder,
                                'metadata': metadata
                            })
                        except Exception as e:
                            print(f"Error processing {file_path}: {str(e)}")
            except Exception as e:
                print(f"Error accessing directory {folder_path}: {str(e)}")
    
    return documents

def create_metadata_file(documents: List[Dict]):
    """Create metadata file for all documents."""
    metadata = []
    
    for doc in documents:
        metadata.append({
            'file_path': doc['file_path'],
            'source_type': doc['source_type'],
            'metadata': doc.get('metadata', {})
        })
    
    metadata_path = 'c:/Users/krish/medical/backend/data/medical_documents/metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)


if __name__ == "__main__":
    setup_data_directories()
    documents = scan_documents()
    create_metadata_file(documents)
