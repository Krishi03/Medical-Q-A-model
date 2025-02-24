import os
from typing import List, Dict, Any
import json
from transformers import AutoTokenizer, AutoModel
import torch
import faiss
import numpy as np

class DocumentProcessor:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("pritamdeka/S-PubMedBert-MS-MARCO")
        self.model = AutoModel.from_pretrained("pritamdeka/S-PubMedBert-MS-MARCO")
        self.chunk_size = 400  # Target tokens per chunk
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    def read_document(self, file_path: str) -> Dict[str, Any]:
        """Read document and separate metadata from content."""
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Extract metadata and content
        metadata = {}
        content_start = 0
        for i, line in enumerate(lines):
            if line.strip() == '---':
                content_start = i + 1
                break
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip().lower()] = value.strip()

        content = ''.join(lines[content_start:]).strip()
        return {'metadata': metadata, 'content': content}

    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks of approximately target token length."""
        tokens = self.tokenizer.encode(text)
        chunks = []
        current_chunk = []
        current_length = 0

        for token in tokens:
            current_chunk.append(token)
            current_length += 1
            
            if current_length >= self.chunk_size:
                chunks.append(self.tokenizer.decode(current_chunk))
                current_chunk = []
                current_length = 0
                
        if current_chunk:
            chunks.append(self.tokenizer.decode(current_chunk))
            
        return chunks

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for text chunks."""
        embeddings = []
        
        with torch.no_grad():
            for text in texts:
                inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                outputs = self.model(**inputs)
                embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
                embeddings.append(embedding[0])
                
        return np.array(embeddings)

    def process_documents(self):
        """Process all documents and create vector store."""
        base_path = 'c:/Users/krish/medical/backend/data/medical_documents'
        processed_data = []
        all_embeddings = []
        
        # Process each document
        for folder in ['clinical_guidelines', 'patient_education']:
            folder_path = os.path.join(base_path, folder)
            for filename in os.listdir(folder_path):
                if filename.endswith('.txt'):
                    file_path = os.path.join(folder_path, filename)
                    doc_data = self.read_document(file_path)
                    chunks = self.chunk_text(doc_data['content'])
                    chunk_embeddings = self.generate_embeddings(chunks)
                    
                    # Store chunk data
                    for i, (chunk, embedding) in enumerate(zip(chunks, chunk_embeddings)):
                        chunk_data = {
                            'chunk_id': f"{filename}_{i}",
                            'text': chunk,
                            'metadata': {
                                **doc_data['metadata'],
                                'source_file': filename,
                                'chunk_index': i
                            }
                        }
                        processed_data.append(chunk_data)
                        all_embeddings.append(embedding)

        # Create FAISS index
        dimension = all_embeddings[0].shape[0]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(all_embeddings))

        # Save processed data and index
        os.makedirs('c:/Users/krish/medical/backend/data/processed', exist_ok=True)
        os.makedirs('c:/Users/krish/medical/backend/data/vector_store', exist_ok=True)

        with open('c:/Users/krish/medical/backend/data/processed/chunks.json', 'w') as f:
            json.dump(processed_data, f, indent=2)

        faiss.write_index(index, 'c:/Users/krish/medical/backend/data/vector_store/document_index.faiss')

if __name__ == "__main__":
    processor = DocumentProcessor()
    processor.process_documents()