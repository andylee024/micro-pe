"""
Wisconsin FDD Scraper

Scrapes Franchise Disclosure Documents (FDDs) from Wisconsin Department of Financial Institutions.
Follows the pattern established in tools/minnesota_fdd.py.

URL: https://apps.dfi.wi.gov/apps/FranchiseSearch/MainSearch.aspx
"""

import json
import os
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from tools.base import Tool


class WisconsinFDDScraper(Tool):
    """Search Wisconsin DFI for FDD documents"""

    BASE_URL = "https://apps.dfi.wi.gov/apps/FranchiseSearch/MainSearch.aspx"
    CACHE_TTL_DAYS = 90

    def __init__(self):
        super().__init__()
        self.cache_dir = Path("cache/wisconsin_fdd")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_dir = self.cache_dir / "pdfs"
        self.pdf_dir.mkdir(exist_ok=True)

    def _get_chrome_driver(self):
        """
        Initialize Chrome driver with anti-detection measures.
        Copied from minnesota_fdd.py pattern.
        """
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Anti-detection: Override webdriver property
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
            },
        )

        return driver

    def _get_cache_key(self, industry: str, max_results: int) -> str:
        """Generate cache key for search query"""
        safe_industry = industry.replace(" ", "_").lower()
        return f"wisconsin_{safe_industry}_{max_results}"

    def _is_cache_valid(self, cache_file: Path) -> bool:
        """Check if cache file exists and is within TTL"""
        if not cache_file.exists():
            return False

        # Check file age
        file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        age = datetime.now() - file_time
        return age < timedelta(days=self.CACHE_TTL_DAYS)

    def _load_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Load cached results if valid"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if self._is_cache_valid(cache_file):
            with open(cache_file, "r") as f:
                return json.load(f)
        return None

    def _save_cache(self, cache_key: str, data: Dict[str, Any]):
        """Save results to cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, "w") as f:
            json.dump(data, f, indent=2)

    def _fill_search_form(self, driver, industry: str):
        """
        Fill and submit the Wisconsin FDD search form.
        ASP.NET form with ctl00_ prefixed IDs.
        """
        # Navigate to search page
        driver.get(self.BASE_URL)
        time.sleep(2)

        # Wait for search input to be present
        wait = WebDriverWait(driver, 10)
        search_input = wait.until(
            EC.presence_of_element_located(
                (By.ID, "ctl00_MainContent_txtSearch")
            )
        )

        # Fill search form
        search_input.clear()
        search_input.send_keys(industry)

        # Click search button
        search_button = driver.find_element(
            By.ID, "ctl00_MainContent_btnSearch"
        )
        search_button.click()

        # Wait for results to load
        time.sleep(random.uniform(3.0, 5.0))

    def _parse_gridview_results(
        self, driver, max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Parse ASP.NET GridView results table.

        Table structure:
        Cell[0] = Franchise Name
        Cell[1] = Document ID
        Cell[2] = PDF Link (<a> tag with href)
        Cell[3] = Filing Year
        """
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find results table
        table = soup.find("table", id="ctl00_MainContent_gvResults")
        if not table:
            return []

        results = []
        rows = table.find_all("tr", class_="GridRowStyle")

        for row in rows[:max_results]:
            try:
                cells = row.find_all("td")
                if len(cells) < 4:
                    continue

                # Extract data from cells
                franchise_name = cells[0].get_text(strip=True)
                document_id = cells[1].get_text(strip=True)

                # Get PDF link
                pdf_link_tag = cells[2].find("a")
                if pdf_link_tag and pdf_link_tag.get("href"):
                    pdf_url = urljoin(self.BASE_URL, pdf_link_tag["href"])
                else:
                    pdf_url = None

                # Get filing year
                year_text = cells[3].get_text(strip=True)
                try:
                    fdd_year = int(year_text)
                except (ValueError, TypeError):
                    fdd_year = None

                result = {
                    "franchise_name": franchise_name,
                    "document_id": document_id,
                    "pdf_url": pdf_url,
                    "fdd_year": fdd_year,
                    "source_url": self.BASE_URL,
                }

                results.append(result)

            except Exception as e:
                print(f"⚠️  Error parsing row: {e}")
                continue

        return results

    def _download_pdf(self, pdf_url: str, franchise_name: str, document_id: str) -> Optional[str]:
        """
        Download PDF file via direct HTTP request.
        Wisconsin allows direct downloads (simpler than Minnesota's session-based approach).

        Args:
            pdf_url: URL to download PDF from
            franchise_name: Name of franchise (for filename)
            document_id: Document ID (for filename)

        Returns:
            Path to downloaded PDF file, or None if download failed
        """
        try:
            # Create safe filename
            safe_name = "".join(
                c for c in franchise_name if c.isalnum() or c in (" ", "-", "_")
            ).strip()
            safe_name = safe_name.replace(" ", "_")
            filename = f"{safe_name}_{document_id}.pdf"
            filepath = self.pdf_dir / filename

            # Skip if already downloaded
            if filepath.exists():
                print(f"✓ PDF already cached: {filename}")
                return str(filepath)

            # Download PDF with httpx
            print(f"⬇️  Downloading PDF: {filename}")
            with httpx.Client(follow_redirects=True, timeout=30.0) as client:
                response = client.get(pdf_url)
                response.raise_for_status()

                # Save PDF
                with open(filepath, "wb") as f:
                    f.write(response.content)

                print(f"✓ Downloaded: {filename} ({len(response.content)} bytes)")
                return str(filepath)

        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP error downloading PDF: {e.response.status_code}")
            return None
        except httpx.TimeoutException:
            print(f"❌ Timeout downloading PDF from {pdf_url}")
            return None
        except Exception as e:
            print(f"❌ Error downloading PDF: {e}")
            return None

    def search(
        self,
        industry: str,
        max_results: int = 10,
        download_pdfs: bool = True,
        extract_item19: bool = True,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Search Wisconsin DFI for FDD documents.

        Args:
            industry: Industry or franchise name to search for
            max_results: Maximum number of results to return
            download_pdfs: Whether to download PDF files
            extract_item19: Whether to extract Item 19 from PDFs (requires download_pdfs=True)
            use_cache: Whether to use cached results

        Returns:
            Dictionary with search results:
            {
                "source": "wisconsin_dfi",
                "search_date": "2026-02-17T...",
                "industry": "car wash",
                "total_found": 12,
                "results": [...]
            }
        """
        # Check cache first
        cache_key = self._get_cache_key(industry, max_results)
        if use_cache:
            cached = self._load_cache(cache_key)
            if cached:
                print(f"✓ Using cached results for '{industry}'")
                return cached

        driver = None
        try:
            print(f"🔍 Searching Wisconsin DFI for '{industry}'...")

            # Initialize Chrome driver
            driver = self._get_chrome_driver()

            # Fill and submit search form
            self._fill_search_form(driver, industry)

            # Parse results
            results = self._parse_gridview_results(driver, max_results)

            print(f"✓ Found {len(results)} results")

            # Download PDFs if requested
            if download_pdfs:
                print(f"⬇️  Downloading {len(results)} PDFs...")
                for result in results:
                    if result.get("pdf_url"):
                        pdf_path = self._download_pdf(
                            result["pdf_url"],
                            result["franchise_name"],
                            result["document_id"],
                        )
                        result["pdf_downloaded"] = pdf_path is not None
                        result["pdf_path"] = pdf_path
                    else:
                        result["pdf_downloaded"] = False
                        result["pdf_path"] = None

            # TODO: Extract Item 19 if requested (next task)
            if extract_item19 and download_pdfs:
                print("⚠️  Item 19 extraction not yet implemented")

            # Build response
            response = {
                "source": "wisconsin_dfi",
                "search_date": datetime.now().isoformat(),
                "industry": industry,
                "total_found": len(results),
                "results": results,
            }

            # Save to cache
            self._save_cache(cache_key, response)

            return response

        except Exception as e:
            print(f"❌ Error during Wisconsin FDD search: {e}")
            return {
                "source": "wisconsin_dfi",
                "search_date": datetime.now().isoformat(),
                "industry": industry,
                "total_found": 0,
                "results": [],
                "error": str(e),
            }

        finally:
            if driver:
                driver.quit()


# Test function for development
def _test_wisconsin_scraper():
    """Test the Wisconsin FDD scraper"""
    scraper = WisconsinFDDScraper()

    # Test search
    results = scraper.search(
        industry="car wash",
        max_results=5,
        download_pdfs=True,
        use_cache=False,
    )

    print(f"\n{'='*60}")
    print(f"Total found: {results['total_found']}")
    print(f"{'='*60}\n")

    for i, result in enumerate(results["results"], 1):
        print(f"{i}. {result['franchise_name']}")
        print(f"   Document ID: {result['document_id']}")
        print(f"   Year: {result['fdd_year']}")
        print(f"   PDF URL: {result['pdf_url']}")
        print(f"   PDF Downloaded: {result.get('pdf_downloaded', False)}")
        if result.get("pdf_path"):
            print(f"   PDF Path: {result['pdf_path']}")
        print()


if __name__ == "__main__":
    _test_wisconsin_scraper()
