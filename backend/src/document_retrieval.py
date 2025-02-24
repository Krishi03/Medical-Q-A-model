import faiss
import json
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from typing import List, Dict, Tuple

class DocumentRetrieval:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("pritamdeka/S-PubMedBert-MS-MARCO")
        self.model = AutoModel.from_pretrained("pritamdeka/S-PubMedBert-MS-MARCO")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
        # Load FAISS index and chunks
        self.index = faiss.read_index('c:/Users/krish/medical/backend/data/vector_store/document_index.faiss')
        with open('c:/Users/krish/medical/backend/data/processed/chunks.json', 'r') as f:
            self.chunks = json.load(f)

    def generate_query_embedding(self, query: str) -> np.ndarray:
        """Generate embedding for the query text."""
        with torch.no_grad():
            inputs = self.tokenizer(query, return_tensors="pt", padding=True, truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
        return embedding

    def calculate_cosine_similarity(self, query_embedding: np.ndarray, chunk_embedding: np.ndarray) -> float:
        """Calculate cosine similarity between query and chunk embeddings."""
        # Reshape embeddings to 1D arrays
        query_embedding = query_embedding.flatten()
        chunk_embedding = chunk_embedding.flatten()
        return np.dot(query_embedding, chunk_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
        )
    def retrieve_relevant_chunks(self, query: str, k: int = 5) -> List[Dict]:
        """Retrieve top-k relevant chunks for the given query."""
        # Generate query embedding
        query_embedding = self.generate_query_embedding(query)
        
        # Get initial candidates using FAISS
        distances, indices = self.index.search(query_embedding, k * 2)
        
        # Calculate cosine similarity for better accuracy
        results = []
        cosine_threshold = 0.4  # Adjust this threshold based on testing
        
        for idx in indices[0]:
            chunk = self.chunks[idx]
            chunk_embedding = self.generate_query_embedding(chunk['text'])
            
            # Calculate cosine similarity directly
            similarity = self.calculate_cosine_similarity(
                query_embedding,
                chunk_embedding
            )
            
            if similarity >= cosine_threshold:
                results.append({
                    'chunk_id': chunk['chunk_id'],
                    'text': chunk['text'],
                    'metadata': chunk['metadata'],
                    'similarity_score': float(similarity)
                })
        
        # Sort by cosine similarity and take top k
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:k]
        # Re-rank results by cosine similarity
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        for result in results:
            print(result['similarity_score'])
        return results

    def rebuild_index(self) -> None:
        """Rebuild FAISS index with updated documents."""
        try:
            # Generate embeddings for all chunks
            embeddings = []
            updated_chunks = []
            
            # Process each chunk
            for chunk in self.chunks:
                with torch.no_grad():
                    inputs = self.tokenizer(
                        chunk['text'],
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                        max_length=512
                    )
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    outputs = self.model(**inputs)
                    embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
                    embeddings.append(embedding)
                    updated_chunks.append(chunk)

            # Convert embeddings to numpy array
            embeddings_array = np.vstack(embeddings)

            # Build new FAISS index
            dimension = embeddings_array.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings_array)

            # Save updated index and chunks
            faiss.write_index(self.index, 'c:/Users/krish/medical/backend/data/vector_store/document_index.faiss')
            with open('c:/Users/krish/medical/backend/data/processed/chunks.json', 'w') as f:
                json.dump(updated_chunks, f)

        except Exception as e:
            print(f"Error rebuilding index: {str(e)}")
            raise
# Example usage
if __name__ == "__main__":
    retriever = DocumentRetrieval()
    query = "What are the treatment options for severe asthma?"
    results = retriever.retrieve_relevant_chunks(query)
    
    print(f"Top results for query: {query}\n")
    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"Similarity Score: {result['similarity_score']:.4f}")
        print(f"Source: {result['metadata']['source_file']}")
        print(f"Text: {result['text'][:200]}...")
        print("-" * 80)