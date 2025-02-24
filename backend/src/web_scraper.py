import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote
from typing import List, Dict
import time
import os

class MedicalWebScraper:
    def __init__(self):
        self.trusted_domains = {
            'medlineplus.gov': 'https://medlineplus.gov/search.html?q=',
            'mayoclinic.org': 'https://www.mayoclinic.org/search/search-results?q=',
            'who.int': 'https://www.who.int/search?q=',
            'nih.gov': 'https://search.nih.gov/search?q=',
            'cdc.gov': 'https://search.cdc.gov/search?q='
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def search_medical_sites(self, query: str) -> List[str]:
        """Search trusted medical sites for the query and return relevant URLs"""
        relevant_urls = []
        encoded_query = quote(query)
        
        for domain, search_url in self.trusted_domains.items():
            try:
                search_response = requests.get(
                    f"{search_url}{encoded_query}",
                    headers=self.headers,
                    timeout=10
                )
                search_response.raise_for_status()
                soup = BeautifulSoup(search_response.text, 'html.parser')
                
                # Find result links (customize selectors for each domain)
                if 'mayoclinic.org' in domain:
                    links = soup.select('.search-results a')
                elif 'medlineplus.gov' in domain:
                    links = soup.select('.search-results-list a')
                else:
                    links = soup.find_all('a', href=True)
                
                # Get first relevant result
                for link in links:
                    href = link.get('href', '')
                    if domain in href and not any(skip in href.lower() for skip in ['search', 'image', 'video']):
                        relevant_urls.append(href)
                        break
                
                time.sleep(2)  # Respect rate limits
            except Exception as e:
                print(f"Error searching {domain}: {str(e)}")
                continue
        
        return relevant_urls

    def scrape_medical_content(self, url: str) -> Dict:
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract main content (customize selectors based on the website)
            content = ""
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            if main_content:
                content = main_content.get_text(separator='\n', strip=True)

            return {
                'url': url,
                'content': content,
                'source': urlparse(url).netloc,
                'timestamp': time.strftime('%Y-%m-%d')
            }
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None

    def save_to_document(self, data: Dict) -> str:
        """Save scraped content as a document in the medical_documents folder"""
        filename = f"web_{int(time.time())}.txt"
        filepath = os.path.join('c:/Users/krish/medical/backend/data/medical_documents/web_content', filename)
        
        content = (
            f"Title: {data['url']}\n"
            f"Source: {data['source']}\n"
            f"Date: {data['timestamp']}\n"
            f"Type: Web Content\n\n"
            f"{data['content']}\n"
        )
        
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Saved content to: {filepath}")  # Debug log
            return filepath
        except Exception as e:
            print(f"Error saving content: {str(e)}")
            return None
        return filepath

    def process_urls(self, urls: List[str]) -> List[str]:
        """Process multiple URLs and return paths to saved documents"""
        document_paths = []
        
        for url in urls:
            if not any(domain in url for domain in self.trusted_domains):
                print(f"Skipping untrusted domain: {url}")
                continue
                
            data = self.scrape_medical_content(url)
            if data:
                doc_path = self.save_to_document(data)
                document_paths.append(doc_path)
        
        return document_paths

    def process_query(self, query: str) -> List[str]:
        """Process a query by searching and scraping relevant content"""
        print(f"Searching medical sites for: {query}")  # Debug log
        # Search for relevant URLs
        relevant_urls = self.search_medical_sites(query)
        print(f"Found URLs: {relevant_urls}")  # Debug log
        
        # Process found URLs
        document_paths = self.process_urls(relevant_urls)
        print(f"Processed documents: {document_paths}")  # Debug log
        return document_paths