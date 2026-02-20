"""
Wisconsin FDD Scraper

Scrapes Franchise Disclosure Documents from Wisconsin Department of Financial Institutions.
URL: https://apps.dfi.wi.gov/apps/FranchiseSearch/MainSearch.aspx

Follows the pattern from tools/minnesota_fdd.py (reference implementation).
"""

import os
import time
import random
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import httpx
import fitz  # PyMuPDF

from core.base import Tool


class WisconsinFDDScraper(Tool):
    """Search Wisconsin DFI for FDD documents"""

    BASE_URL = "https://apps.dfi.wi.gov/apps/FranchiseSearch/MainSearch.aspx"
    CACHE_TTL_DAYS = 90
    
    def __init__(self):
        super().__init__()
        self.cache_dir = Path("cache/wisconsin_fdd")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.pdf_dir = Path("data/wisconsin_fdds")
        self.pdf_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, industry: str, max_results: int, download_pdfs: bool, extract_item19: bool) -> str:
        """Generate cache key from search parameters"""
        params = f"{industry}_{max_results}_{download_pdfs}_{extract_item19}"
        return hashlib.md5(params.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for given key"""
        return self.cache_dir / f"{cache_key}.json"

    def _load_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Load cached results if valid"""
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)
            
            # Check if cache is still valid
            cache_date = datetime.fromisoformat(cached_data['search_date'])
            age_days = (datetime.now() - cache_date).days
            
            if age_days < self.CACHE_TTL_DAYS:
                print(f"✓ Using cached results (age: {age_days} days)")
                return cached_data
            else:
                print(f"⚠ Cache expired (age: {age_days} days)")
                return None
                
        except Exception as e:
            print(f"⚠ Cache load error: {e}")
            return None

    def _save_cache(self, cache_key: str, data: Dict[str, Any]):
        """Save results to cache"""
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✓ Cached results to {cache_path}")
        except Exception as e:
            print(f"⚠ Cache save error: {e}")

    def _setup_chrome_driver(self) -> webdriver.Chrome:
        """Setup Chrome driver with anti-detection measures"""
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Anti-detection: Override navigator.webdriver
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
        
        return driver

    def _fill_search_form(self, driver: webdriver.Chrome, industry: str):
        """Fill and submit the Wisconsin FDD search form"""
        # Navigate to URL
        driver.get(self.BASE_URL)
        time.sleep(2)

        # Wait for search input to be present
        wait = WebDriverWait(driver, 10)
        search_input = wait.until(
            EC.presence_of_element_located((By.ID, "txtName"))
        )

        # Fill search form
        search_input.clear()
        search_input.send_keys(industry)

        # Click search button
        search_button = driver.find_element(By.ID, "btnSearch")
        search_button.click()

        # Wait for results to load
        time.sleep(3)

    def _parse_results(self, driver: webdriver.Chrome, max_results: int) -> List[Dict[str, Any]]:
        """Parse search results from results table"""
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find results table (new structure: id='grdSearchResults')
        table = soup.find('table', id='grdSearchResults')
        if not table:
            print("⚠ No results table found")
            return []

        # Find all result rows (new classes: SearchResultsOddRow/SearchResultsEvenRow)
        odd_rows = table.find_all('tr', class_='SearchResultsOddRow')
        even_rows = table.find_all('tr', class_='SearchResultsEvenRow')
        all_rows = odd_rows + even_rows

        # Sort by document order (they're already in order, but just to be safe)
        all_rows = sorted(all_rows, key=lambda row: int(row.find_all('td')[0].get_text(strip=True)) if row.find_all('td') else 0, reverse=True)

        results = []
        for row in all_rows[:max_results]:
            try:
                cells = row.find_all('td')
                if len(cells) < 7:
                    continue

                # New column structure:
                # cells[0] = File Number
                # cells[1] = Legal Name
                # cells[2] = Trade Name
                # cells[3] = Effective Date (e.g., "4/30/2025")
                # cells[4] = Expiration Date
                # cells[5] = Status
                # cells[6] = Details link

                file_number = cells[0].get_text(strip=True)
                legal_name = cells[1].get_text(strip=True)
                trade_name = cells[2].get_text(strip=True)
                effective_date = cells[3].get_text(strip=True)
                status = cells[5].get_text(strip=True)

                # Use trade name if available, otherwise legal name
                franchise_name = trade_name if trade_name else legal_name

                # Extract year from effective date (e.g., "4/30/2025" → 2025)
                year = None
                if effective_date and '/' in effective_date:
                    try:
                        year = int(effective_date.split('/')[-1])
                    except ValueError:
                        pass

                # Extract details URL (leads to page with FDD PDF)
                details_link = cells[6].find('a')
                details_url = None
                if details_link and details_link.get('href'):
                    details_url = details_link['href']
                    # Make absolute URL
                    if not details_url.startswith('http'):
                        details_url = f"https://apps.dfi.wi.gov/apps/FranchiseSearch/{details_url}"

                # Only include records with valid details URL (skip expired records without links)
                if not details_url:
                    continue

                result = {
                    'franchise_name': franchise_name,
                    'legal_name': legal_name,
                    'trade_name': trade_name,
                    'document_id': file_number,
                    'effective_date': effective_date,
                    'status': status,
                    'pdf_url': details_url,  # This is actually the details page, not direct PDF
                    'fdd_year': year,
                    'source_url': self.BASE_URL
                }

                results.append(result)

            except Exception as e:
                print(f"⚠ Error parsing row: {e}")
                continue

        return results

    def _download_pdf(self, pdf_url: str, franchise_name: str, document_id: str) -> Optional[str]:
        """Download PDF from URL"""
        if not pdf_url:
            return None
        
        try:
            # Create safe filename
            safe_name = "".join(c for c in franchise_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            filename = f"{safe_name}_{document_id}.pdf"
            filepath = self.pdf_dir / filename
            
            # Skip if already downloaded
            if filepath.exists():
                print(f"✓ PDF already exists: {filename}")
                return str(filepath)
            
            # Download PDF
            print(f"⬇ Downloading PDF: {filename}")
            response = httpx.get(pdf_url, follow_redirects=True, timeout=30.0)
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"✓ Downloaded: {filename}")
                return str(filepath)
            else:
                print(f"⚠ Download failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠ PDF download error: {e}")
            return None

    def _extract_item19(self, pdf_path: str) -> Optional[Dict[str, Any]]:
        """Extract Item 19 (Financial Performance Representations) from FDD PDF"""
        if not pdf_path or not os.path.exists(pdf_path):
            return None
        
        try:
            doc = fitz.open(pdf_path)
            item19_text = []
            found_item19 = False
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                # Look for Item 19 header
                if not found_item19 and 'ITEM 19' in text.upper():
                    found_item19 = True
                    item19_text.append(text)
                    continue
                
                # If we found Item 19, keep collecting until Item 20
                if found_item19:
                    if 'ITEM 20' in text.upper():
                        break
                    item19_text.append(text)
            
            doc.close()
            
            if item19_text:
                full_text = '\n'.join(item19_text)
                return {
                    'has_item_19': True,
                    'item_19_text': full_text[:5000],  # Limit size
                    'item_19_length': len(full_text)
                }
            else:
                return {
                    'has_item_19': False,
                    'item_19_text': None,
                    'item_19_length': 0
                }
                
        except Exception as e:
            print(f"⚠ Item 19 extraction error: {e}")
            return None

    def search(
        self,
        industry: str,
        max_results: int = 10,
        download_pdfs: bool = True,
        extract_item19: bool = True,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Search Wisconsin DFI for FDD documents.
        
        Args:
            industry: Industry keyword to search for
            max_results: Maximum number of results to return
            download_pdfs: Whether to download PDF files
            extract_item19: Whether to extract Item 19 from PDFs
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary containing search results and metadata
        """
        # Check cache first
        cache_key = self._get_cache_key(industry, max_results, download_pdfs, extract_item19)
        
        if use_cache:
            cached_data = self._load_cache(cache_key)
            if cached_data:
                return cached_data
        
        print(f"🔍 Searching Wisconsin DFI for: {industry}")
        
        driver = None
        try:
            # Setup driver
            driver = self._setup_chrome_driver()
            
            # Fill search form
            self._fill_search_form(driver, industry)
            
            # Parse results
            results = self._parse_results(driver, max_results)
            
            print(f"✓ Found {len(results)} results")
            
            # Download PDFs and extract Item 19 if requested
            if download_pdfs:
                for result in results:
                    if result.get('pdf_url'):
                        pdf_path = self._download_pdf(
                            result['pdf_url'],
                            result['franchise_name'],
                            result['document_id']
                        )
                        result['pdf_downloaded'] = pdf_path is not None
                        result['local_pdf_path'] = pdf_path  # Use local_pdf_path to match test expectations

                        if extract_item19 and pdf_path:
                            item19_data = self._extract_item19(pdf_path)
                            if item19_data:
                                result.update(item19_data)

                        # Rate limiting
                        time.sleep(random.uniform(1.0, 2.0))
            
            # Build response
            response = {
                'source': 'wisconsin_dfi',
                'search_date': datetime.now().isoformat(),
                'industry': industry,
                'total_found': len(results),
                'results': results
            }
            
            # Save to cache
            if use_cache:
                self._save_cache(cache_key, response)
            
            return response
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return {
                'source': 'wisconsin_dfi',
                'search_date': datetime.now().isoformat(),
                'industry': industry,
                'total_found': 0,
                'results': [],
                'error': str(e)
            }
            
        finally:
            if driver:
                driver.quit()


# Test function
if __name__ == "__main__":
    scraper = WisconsinFDDScraper()
    results = scraper.search("car wash", max_results=5)
    print(json.dumps(results, indent=2))
