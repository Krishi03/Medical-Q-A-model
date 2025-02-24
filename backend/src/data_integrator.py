import os
from typing import List
from document_retrieval import DocumentRetrieval
from web_scraper import MedicalWebScraper
from data_organisation import setup_data_directories, scan_documents, create_metadata_file

class DataIntegrator:
    def __init__(self):
        self.scraper = MedicalWebScraper()
        self.retriever = DocumentRetrieval()
        setup_data_directories()

    def integrate_web_content(self, query: str) -> None:
        """Scrape and integrate web content with existing data"""
        try:
            
            new_docs = self.scraper.process_query(query)
            
            if new_docs:  
                print(f"New documents found: {len(new_docs)}")
                # Update metadata
                documents = scan_documents()
                create_metadata_file(documents)
                
                
                self.retriever.rebuild_index()
            else:
                print("No new documents found from web scraping")
                
        except Exception as e:
            print(f"Error in web content integration: {str(e)}")

    def update_trusted_sources(self, urls: List[str]) -> None:
        """Add new trusted sources and update content"""
        self.integrate_web_content(urls)
