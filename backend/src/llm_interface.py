import os
from typing import List, Dict
import google.generativeai as genai
from document_retrieval import DocumentRetrieval
from data_integrator import DataIntegrator

class LLMInterface:
    def __init__(self, api_key: str = None):
        # Try to get API key from parameter, then environment, or raise error
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Google API key is required. Either pass it as a parameter or "
                "set the GOOGLE_API_KEY environment variable."
            )
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.0-pro')
        self.retriever = DocumentRetrieval()
        self.data_integrator = DataIntegrator()

    def update_knowledge_base(self, urls: List[str]) -> None:
        """Update the knowledge base with new web content"""
        self.data_integrator.integrate_web_content(urls)

    def format_prompt(self, query: str, relevant_chunks: List[Dict]) -> str:
        """Format the prompt with context and instructions."""
        local_contexts = []
        web_contexts = []
        local_refs = []
        web_refs = []
        
        for chunk in relevant_chunks:
            if 'web_content' in chunk['metadata']['source_file']:
                web_contexts.append(chunk['text'])
                web_refs.append(f"Web Source: {chunk['metadata'].get('url', '')}")
            else:
                local_contexts.append(chunk['text'])
                doc_name = os.path.basename(chunk['metadata']['source_file'])
                local_refs.append(f"Local Document: {doc_name}")

        separator = '-' * 80
        
        prompt = (
            f'Please answer the following medical question: "{query}"\n\n'
            f'Context from local medical documents:\n'
            f'{separator}\n'
            f'{chr(10).join(local_contexts)}\n'
            f'{separator}\n\n'
            f'Additional context from web sources:\n'
            f'{separator}\n'
            f'{chr(10).join(web_contexts)}\n'
            f'{separator}\n\n'
            f'Instructions:\n'
            f'1. First use information from local medical documents if available.\n'
            f'2. Supplement with web-sourced information as needed.\n'
            f'3. Include ALL references used (both local and web).\n'
            f'4. Format your response with:\n'
            f'   - Answer\n'
            f'   - References (list both local documents and web sources)\n'
            f'   - Follow-up Questions\n'
            f'   - Medical Disclaimers\n\n'
            f'Available References:\n'
            f'Local Documents:\n{chr(10).join(local_refs)}\n\n'
            f'Web Sources:\n{chr(10).join(web_refs)}\n\n'
            f'Answer:'
        )
        return prompt

    def generate_response(self, query: str, max_chunks: int = 5) -> Dict:
        """Generate a response using the Gemini model."""
        try:
            # First get relevant chunks from existing documents
            local_chunks = self.retriever.retrieve_relevant_chunks(query, k=max_chunks)
            
            # Then update knowledge base with web content
            self.data_integrator.integrate_web_content(query)
            
            # Get chunks again to include both local and web content
            all_chunks = self.retriever.retrieve_relevant_chunks(query, k=max_chunks)
            
            # Format prompt with all available context
            prompt = self.format_prompt(query, all_chunks)
            
            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            
            return {
                'answer': response.text,
                'context_chunks': all_chunks,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'answer': f"An error occurred: {str(e)}",
                'context_chunks': [],
                'status': 'error'
            }

# Example usage
if __name__ == "__main__":
    # Replace with your actual Google API key
    api_key = "AIzaSyBNW_rLfDKbjxC5gop7z59PCJkjztRYd9A"
    llm_interface = LLMInterface(api_key=api_key)
    query = "What are the treatment options for severe asthma?"
    response = llm_interface.generate_response(query)
    
    print("Query:", query)
    print("\nResponse:", response['answer'])