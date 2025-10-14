import requests
from bs4 import BeautifulSoup
import pdfplumber
from typing import List, Dict, Tuple
import logging
import io
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentScraper:
    """
    Scrapes quarterly reports and earnings transcripts from screener.in
    """
    
    def __init__(self):
        self.base_url = "https://www.screener.in"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def get_tcs_documents(self, num_quarters: int = 2) -> Dict[str, List[Dict]]:
        """
        Fetch latest quarterly reports and transcripts for TCS
        
        Returns:
            Dictionary with 'reports' and 'transcripts' keys containing document data
        """
        try:
            url = f"{self.base_url}/company/TCS/consolidated/#documents"
            logger.info(f"Fetching documents from {url}")
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            quarterly_reports = self._extract_quarterly_reports(soup, num_quarters)
            transcripts = self._extract_transcripts(soup, num_quarters)
            
            logger.info(f"Found {len(quarterly_reports)} reports and {len(transcripts)} transcripts")
            
            return {
                "reports": quarterly_reports,
                "transcripts": transcripts
            }
            
        except Exception as e:
            logger.error(f"Error scraping documents: {str(e)}")
            raise
    
    def _extract_quarterly_reports(self, soup: BeautifulSoup, num_quarters: int) -> List[Dict]:
        """Extract quarterly report links and metadata"""
        reports = []
        
        try:
            document_section = soup.find('section', {'id': 'documents'})
            if not document_section:
                logger.warning("Documents section not found")
                return reports
            
            report_links = document_section.find_all('a', href=True, limit=num_quarters * 2)
            
            for link in report_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if any(keyword in text.lower() for keyword in ['quarterly', 'q1', 'q2', 'q3', 'q4', 'results']):
                    if href.startswith('/'):
                        href = self.base_url + href
                    
                    reports.append({
                        'title': text,
                        'url': href,
                        'type': 'quarterly_report'
                    })
                    
                    if len(reports) >= num_quarters:
                        break
            
        except Exception as e:
            logger.error(f"Error extracting quarterly reports: {str(e)}")
        
        return reports
    
    def _extract_transcripts(self, soup: BeautifulSoup, num_quarters: int) -> List[Dict]:
        """Extract earnings call transcript links"""
        transcripts = []
        
        try:
            document_section = soup.find('section', {'id': 'documents'})
            if not document_section:
                return transcripts
            
            transcript_links = document_section.find_all('a', href=True)
            
            for link in transcript_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if any(keyword in text.lower() for keyword in ['transcript', 'concall', 'earnings call']):
                    if href.startswith('/'):
                        href = self.base_url + href
                    
                    transcripts.append({
                        'title': text,
                        'url': href,
                        'type': 'transcript'
                    })
                    
                    if len(transcripts) >= num_quarters:
                        break
            
        except Exception as e:
            logger.error(f"Error extracting transcripts: {str(e)}")
        
        return transcripts
    
    def download_and_extract_text(self, document: Dict) -> str:
        """
        Download document and extract text content
        Handles both PDF and HTML documents
        """
        try:
            url = document['url']
            logger.info(f"Downloading: {document['title']}")
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            content_type = response.headers.get('Content-Type', '').lower()
            
            if 'pdf' in content_type or url.endswith('.pdf'):
                return self._extract_pdf_text(response.content)
            else:
                return self._extract_html_text(response.content)
                
        except Exception as e:
            logger.error(f"Error downloading document {document['title']}: {str(e)}")
            return ""
    
    def _extract_pdf_text(self, pdf_content: bytes) -> str:
        """Extract text from PDF using pdfplumber"""
        try:
            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            return ""
    
    def _extract_html_text(self, html_content: bytes) -> str:
        """Extract text from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text(separator='\n', strip=True)
            return text
        except Exception as e:
            logger.error(f"Error extracting HTML text: {str(e)}")
            return ""
