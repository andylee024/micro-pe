"""Minnesota CARDS FDD Scraper Tool"""

import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urljoin

import fitz  # PyMuPDF
import httpx
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

try:
    from .base import Tool
except ImportError:
    from base import Tool


class MinnesotaFDDScraper(Tool):
    """Scrape FDD documents from Minnesota CARDS database"""

    BASE_URL = "https://www.cards.commerce.state.mn.us/"
    CACHE_TTL_DAYS = 90  # FDDs don't change often

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.output_dir = Path("outputs/fdds")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def search(
        self,
        industry: str,
        max_results: int = 10,
        download_pdfs: bool = True,
        extract_item19: bool = True,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Search for FDDs by industry keyword.

        Args:
            industry: Search keyword (e.g., "car wash")
            max_results: Max FDDs to return
            download_pdfs: Whether to download PDFs
            extract_item19: Whether to extract Item 19 text
            use_cache: Whether to use cached results

        Returns:
            Dict with raw FDD data
        """
        print(f"\n🔍 Searching Minnesota CARDS for: {industry}")
        print(f"   Max results: {max_results}")

        cache_key = f"fdd_{industry.replace(' ', '_')}_{max_results}"

        # Check cache
        if use_cache:
            cached = self.load_cache(cache_key)
            if cached:
                print(f"✅ Using cached results from {cached['cached_at']}")
                return cached["data"]

        # Scrape
        print(f"🌐 Connecting to {self.BASE_URL}...")
        results = self._scrape_fdds(industry, max_results)

        if not results:
            print("⚠️  No FDDs found")
            return self._build_response(industry, [])

        print(f"✅ Found {len(results)} FDDs")

        # Download PDFs if requested
        if download_pdfs and driver:
            print(f"\n📥 Downloading PDFs...")
            for i, fdd in enumerate(results, 1):
                print(f"   [{i}/{len(results)}] {fdd['franchise_name']}...")
                try:
                    self._download_pdf_with_selenium(fdd, driver)
                    print(f"      ✅ Downloaded ({fdd.get('pdf_size_mb', 0):.1f} MB)")
                except Exception as e:
                    print(f"      ❌ Failed: {e}")
                    import traceback
                    traceback.print_exc()

        # Extract Item 19 if requested
        if extract_item19:
            print(f"\n📄 Extracting Item 19 text...")
            for i, fdd in enumerate(results, 1):
                if fdd.get("pdf_path"):
                    print(f"   [{i}/{len(results)}] {fdd['franchise_name']}...")
                    try:
                        self._extract_item19(fdd)
                        if fdd.get("has_item_19"):
                            print(f"      ✅ Found Item 19 ({fdd['item_19_length']} chars)")
                        else:
                            print(f"      ⚠️  Item 19 not found")
                    except Exception as e:
                        print(f"      ❌ Failed: {e}")

        # Build response
        response = self._build_response(industry, results)

        # Cache results
        if use_cache:
            self.save_cache(cache_key, response, self.CACHE_TTL_DAYS)

        return response

    def _scrape_fdds(self, industry: str, max_results: int) -> List[Dict]:
        """Use Selenium to scrape Minnesota CARDS"""
        results = []

        # Initialize Chrome with webdriver-manager (auto-downloads correct version)
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Additional headers
        options.add_argument('--disable-extensions')
        options.add_argument('--profile-directory=Default')
        options.add_argument('--disable-plugins-discovery')

        driver = None
        try:
            # Auto-install correct Chrome driver version
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

            # Set additional properties to avoid detection
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'
            })
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Navigate to franchise registrations
            search_url = f"{self.BASE_URL}franchise-registrations"
            print(f"   Navigating to: {search_url}")
            driver.get(search_url)

            # Wait and check page
            time.sleep(5)
            print(f"   Current URL: {driver.current_url}")
            print(f"   Page title: {driver.title}")

            # Save screenshot for debugging
            screenshot_path = Path("outputs/cache/debug_screenshot.png")
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            driver.save_screenshot(str(screenshot_path))
            print(f"   📸 Screenshot saved: {screenshot_path}")

            # Try to find the search form
            try:
                franchise_name_input = driver.find_element(By.ID, "franchiseName")
                print(f"   ✅ Found search form!")
            except NoSuchElementException:
                print(f"   ⚠️  Search form not found - page may have redirected")
                # Save page source for inspection
                debug_html = Path("outputs/cache/debug_page_source.html")
                debug_html.write_text(driver.page_source)
                print(f"   💾 Page source saved: {debug_html}")
                return []

            # Fill in search form
            print(f"   Filling search form with: {industry}")

            try:
                # Find and fill the franchise name field
                franchise_name_input = driver.find_element(By.ID, "franchiseName")
                franchise_name_input.clear()
                franchise_name_input.send_keys(industry)

                # Submit the search
                search_button = driver.find_element(By.ID, "searchButton")
                search_button.click()

                print(f"   ⏳ Waiting for results to load...")
                time.sleep(5)  # Wait for HTMX to load results

                # Save page source after search
                debug_file = Path("outputs/cache/minnesota_search_results.html")
                debug_file.parent.mkdir(parents=True, exist_ok=True)
                debug_file.write_text(driver.page_source)
                print(f"   💾 Saved search results to: {debug_file}")

                # Parse results
                soup = BeautifulSoup(driver.page_source, 'html.parser')

                # Look for results table (id="results" is on the table itself)
                table = soup.find('table', id='results')
                if table:
                    print(f"   ✅ Found results table")

                    tbody = table.find('tbody')
                    if tbody:
                        rows = tbody.find_all('tr')
                        print(f"   Found {len(rows)} franchise documents")

                        for row in rows[:max_results]:
                            try:
                                # Get cells
                                cells = row.find_all('td')
                                if len(cells) >= 2:
                                    # First cell has the document link
                                    doc_link = cells[0].find('a', href=True)
                                    # Second cell has the franchisor name
                                    franchisor_name = cells[1].get_text(strip=True)

                                    if doc_link and franchisor_name:
                                        href = doc_link.get('href')
                                        doc_id = doc_link.get_text(strip=True)
                                        title = doc_link.get('title', '')

                                        # Extract year from document ID or title
                                        year = self._extract_year_from_text(doc_id + ' ' + title)

                                        # Build full URL
                                        pdf_url = href if href.startswith('http') else f"{self.BASE_URL.rstrip('/')}{href}"

                                        fdd_info = {
                                            'franchise_name': franchisor_name,
                                            'document_id': doc_id,
                                            'pdf_url': pdf_url,
                                            'fdd_year': year,
                                            'title': title,
                                            'source_url': driver.current_url
                                        }
                                        results.append(fdd_info)
                                        print(f"      ✅ {franchisor_name} ({doc_id})")

                            except Exception as e:
                                print(f"      ⚠️  Error parsing row: {e}")
                                continue
                else:
                    print(f"   ⚠️  No results div found")

                    # Try alternative: look for any PDF links
                    all_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
                    if all_links:
                        print(f"   Found {len(all_links)} PDF links on page")
                        for link in all_links[:max_results]:
                            href = link.get('href')
                            text = link.get_text(strip=True) or 'Unknown Franchise'
                            results.append({
                                'franchise_name': text,
                                'pdf_url': href if href.startswith('http') else f"{self.BASE_URL}{href}",
                                'fdd_year': self._extract_year_from_text(text),
                                'source_url': driver.current_url
                            })

            except NoSuchElementException as e:
                print(f"   ⚠️  Could not find search form element: {e}")
            except Exception as e:
                print(f"   ⚠️  Error during search: {e}")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise
        finally:
            if driver:
                driver.quit()

        return results

    def _download_pdf_with_selenium(self, fdd: Dict, driver):
        """Download PDF using Selenium to preserve session"""
        url = fdd["pdf_url"]
        doc_id = fdd.get('document_id', 'unknown')
        filename = f"{fdd['franchise_name'].replace(' ', '_')}_{doc_id}.pdf"
        path = self.output_dir / filename

        try:
            # Navigate to the PDF URL
            driver.get(url)
            time.sleep(3)  # Wait for download to start

            # Get the page content
            # If it's a PDF, the browser will load it as binary
            # We can access it through execute_cdp_cmd or by reading the source

            # Try to get PDF content using CDP (Chrome DevTools Protocol)
            try:
                # Get the resource content
                resource = driver.execute_cdp_cmd('Page.getResourceContent', {
                    'frameId': driver.execute_cdp_cmd('Page.getResourceTree', {})['frameTree']['frame']['id'],
                    'url': driver.current_url
                })

                if resource.get('content'):
                    import base64
                    pdf_content = base64.b64decode(resource['content']) if resource.get('base64Encoded') else resource['content'].encode()
                    path.write_bytes(pdf_content)

                    fdd["pdf_path"] = str(path)
                    fdd["pdf_size_mb"] = round(len(pdf_content) / 1024 / 1024, 2)
                    return
            except Exception as cdp_error:
                print(f"         CDP method failed: {cdp_error}")

                # Fallback: Try using httpx with cookies from Selenium
                cookies = driver.get_cookies()
                cookie_jar = {}
                for cookie in cookies:
                    cookie_jar[cookie['name']] = cookie['value']

                headers = {
                    "User-Agent": driver.execute_script("return navigator.userAgent"),
                    "Referer": driver.current_url
                }

                response = httpx.get(url, cookies=cookie_jar, headers=headers, timeout=60, follow_redirects=True)
                response.raise_for_status()

                path.write_bytes(response.content)
                fdd["pdf_path"] = str(path)
                fdd["pdf_size_mb"] = round(len(response.content) / 1024 / 1024, 2)

        except Exception as e:
            raise Exception(f"Failed to download PDF: {e}")

    def _download_pdf(self, fdd: Dict):
        """Download PDF with httpx (fallback method)"""
        url = fdd["pdf_url"]
        filename = f"{fdd['franchise_name'].replace(' ', '_')}_{fdd['fdd_year']}.pdf"
        path = self.output_dir / filename

        # Download with retry logic
        for attempt in range(3):
            try:
                response = httpx.get(url, timeout=60, follow_redirects=True)
                response.raise_for_status()
                path.write_bytes(response.content)

                fdd["pdf_path"] = str(path)
                fdd["pdf_size_mb"] = round(path.stat().st_size / 1024 / 1024, 2)
                return
            except Exception as e:
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)

    def _extract_item19(self, fdd: Dict):
        """Extract Item 19 text from PDF"""
        pdf_path = fdd["pdf_path"]

        with fitz.open(pdf_path) as doc:
            full_text = ""
            for page in doc:
                full_text += page.get_text()

        # Find Item 19 section
        item19_text = self._find_item19_section(full_text)

        if item19_text:
            fdd["has_item_19"] = True
            fdd["item_19_text"] = item19_text
            fdd["item_19_length"] = len(item19_text)

            # Save to separate file for easy inspection
            item19_file = Path(fdd["pdf_path"]).with_suffix(".item19.txt")
            item19_file.write_text(item19_text)
        else:
            fdd["has_item_19"] = False
            fdd["item_19_text"] = None
            fdd["item_19_length"] = 0

    def _find_item19_section(self, text: str) -> Optional[str]:
        """Find Item 19 section using pattern matching"""
        # Pattern: ITEM 19 ... ITEM 20 (or end)
        # Try multiple variations
        patterns = [
            r"ITEM\s+19[\s\S]*?(?=ITEM\s+20|$)",
            r"Item\s+19[\s\S]*?(?=Item\s+20|$)",
            r"ITEM\s+19[\s:.-]*FINANCIAL\s+PERFORMANCE[\s\S]*?(?=ITEM\s+20|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()

        return None

    def _extract_year_from_text(self, text: str) -> Optional[int]:
        """Extract year from text (e.g., '2024', 'FDD 2023')"""
        import re
        match = re.search(r'20\d{2}', text)
        if match:
            return int(match.group())
        return None

    def _build_response(self, industry: str, results: List[Dict]) -> Dict[str, Any]:
        """Build standardized response"""
        return {
            "source": "minnesota_cards",
            "search_date": datetime.now().isoformat(),
            "industry": industry,
            "total_found": len(results),
            "results": results
        }


def test_minnesota_scraper():
    """Test the Minnesota FDD scraper"""
    scraper = MinnesotaFDDScraper()

    results = scraper.search(
        industry="car wash",
        max_results=5,
        download_pdfs=False,  # Don't download yet, just explore
        extract_item19=False,
        use_cache=False
    )

    print("\n" + "="*60)
    print("RESULTS:")
    print("="*60)
    print(f"Source: {results['source']}")
    print(f"Search date: {results['search_date']}")
    print(f"Industry: {results['industry']}")
    print(f"Total found: {results['total_found']}")

    if results['results']:
        print(f"\nFDDs found:")
        for fdd in results['results']:
            print(f"  - {fdd['franchise_name']} ({fdd['fdd_year']})")
    else:
        print("\n⚠️  No FDDs found - need to explore site structure")

    return results


if __name__ == "__main__":
    test_minnesota_scraper()
