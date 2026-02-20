"""California DocQNet FDD Scraper - Refactored

Inherits from FDDScraperBase to eliminate code duplication.
Only contains California-specific form filling, parsing, and pagination logic.

California is the largest franchise state (~30% market share).
The database is notoriously slow (7-10 second wait times) and requires:
- Document type filtering (FDD only, not Blackline/Application/etc.)
- Pagination handling for >10 results
"""

import time
from typing import Dict, List
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

from data_sources.fdd.base import FDDScraperBase
from data_sources.shared.config import ScraperConfig


# Document types to filter out (NOT FDDs)
FDD_DOCUMENT_TYPES = {
    "fdd",
    "franchise disclosure document",
}

NON_FDD_DOCUMENT_TYPES = {
    "blackline",
    "application",
    "amendment",
    "renewal",
    "annual report",
    "consent order",
    "exemption",
    "notice",
    "order",
    "registration",
}


class CaliforniaFDDScraper(FDDScraperBase):
    """Scrape FDD documents from California DFPI DocQNet portal"""

    BASE_URL = "https://docqnet.dfpi.ca.gov/search/"
    SOURCE_ID = "california_fdd"

    def __init__(self, **kwargs):
        # Keep legacy cache location expected by tests
        if "cache_dir" not in kwargs:
            kwargs["cache_dir"] = Path("cache/california_fdd")
        super().__init__(**kwargs)

    def _get_cache_key(self, industry: str, max_results: int, download_pdfs: bool, extract_item19: bool) -> str:
        return super()._get_cache_key(
            industry,
            max_results,
            download_pdfs=download_pdfs,
            extract_item19=extract_item19,
        )

    def _scrape_fdds(self, industry: str, max_results: int, **kwargs) -> List[Dict]:
        """
        California-specific scraping logic.

        Only handles:
        - Navigating to California DocQNet
        - Filling search form (with franchise type selection)
        - Waiting for slow database response (7-10 seconds)
        - Parsing results table with document type filtering
        - Handling pagination if needed

        All Selenium setup, PDF download handled by base class.
        """
        driver = None
        results = []

        try:
            # Create driver (from base class)
            driver = self._create_driver()

            # Navigate to California DocQNet
            self.logger.info(f"Navigating to: {self.BASE_URL}")
            driver.get(self.BASE_URL)
            time.sleep(ScraperConfig.PAGE_LOAD_WAIT)

            # Find and fill search form
            name_input = self._find_name_input(driver)
            if not name_input:
                self.logger.warning("Search form not found")
                self._save_debug_artifacts(driver, "form_not_found")
                return []

            # Fill search
            self.logger.debug(f"Searching for: {industry}")
            name_input.clear()
            name_input.send_keys(industry)

            # Try to select franchise from application type dropdown
            self._select_franchise_type(driver)

            # Submit search
            self._submit_search(driver, name_input)

            # California database is VERY slow - wait 7-10 seconds
            self.logger.info("Waiting for slow CA database response (7-10 seconds)...")
            time.sleep(ScraperConfig.SLOW_WAIT_SECONDS)

            # Parse results
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            results = self._parse_results_table(soup, max_results)

            # Filter FDD documents only
            results = self._filter_fdd_documents(results)

            self.logger.info(f"Parsed {len(results)} FDD documents (after filtering)")

        except Exception as e:
            self.logger.error(f"Scraping failed: {e}", exc_info=True)
            if driver:
                self._save_debug_artifacts(driver, "error")

        finally:
            if driver:
                driver.quit()

        return results

    def _find_name_input(self, driver) -> any:
        """Find name search input with multiple fallback selectors"""
        selectors = [
            (By.ID, "FranchiseName"),
            (By.ID, "franchiseName"),
            (By.ID, "legalName"),
            (By.ID, "LegalName"),
            (By.NAME, "FranchiseName"),
            (By.NAME, "legalName"),
            (By.CSS_SELECTOR, "input[placeholder*='Legal Name']"),
            (By.CSS_SELECTOR, "input[placeholder*='legal name']"),
            (By.CSS_SELECTOR, "input[placeholder*='Name']"),
        ]

        for by, selector in selectors:
            try:
                element = driver.find_element(by, selector)
                if element.is_displayed():
                    self.logger.debug(f"Found name input via: {by}='{selector}'")
                    return element
            except NoSuchElementException:
                continue

        # Fallback: find first visible text input
        try:
            all_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
            for inp in all_inputs:
                if inp.is_displayed():
                    self.logger.debug("Found name input via fallback (first visible)")
                    return inp
        except Exception:
            pass

        return None

    def _select_franchise_type(self, driver):
        """Try to select franchise from application type dropdown"""
        selectors = [
            (By.ID, "ApplicationType"),
            (By.ID, "applicationType"),
            (By.ID, "ddlApplicationType"),
            (By.NAME, "ApplicationType"),
            (By.CSS_SELECTOR, "select"),
        ]

        for by, selector in selectors:
            try:
                dropdown = driver.find_element(by, selector)
                if dropdown.is_displayed() and dropdown.tag_name == "select":
                    select = Select(dropdown)
                    # Try to select a franchise-related option
                    for option in select.options:
                        if "franchise" in option.text.lower():
                            select.select_by_visible_text(option.text)
                            self.logger.debug(f"Selected application type: {option.text}")
                            return
            except Exception:
                continue

    def _submit_search(self, driver, name_input):
        """Find and click search button"""
        selectors = [
            (By.ID, "searchButton"),
            (By.ID, "btnSearch"),
            (By.ID, "SearchButton"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.CSS_SELECTOR, "input[type='submit']"),
            (By.CSS_SELECTOR, "button.btn-primary"),
            (By.XPATH, "//button[contains(text(),'Search')]"),
        ]

        for by, selector in selectors:
            try:
                button = driver.find_element(by, selector)
                if button.is_displayed():
                    button.click()
                    self.logger.debug("Submitted search via button")
                    return
            except NoSuchElementException:
                continue

        # Fallback: submit form directly
        name_input.submit()
        self.logger.debug("Submitted search via form submit")

    def _parse_results_table(self, soup: BeautifulSoup, max_results: int) -> List[Dict]:
        """
        Parse California DocQNet results table.

        Args:
            soup: BeautifulSoup object of results page
            max_results: Maximum results to return

        Returns:
            List of FDD dicts (before document type filtering)
        """
        results = []

        # Find results table (DocQNet uses class 'table' or 'results')
        table = soup.find('table', class_='table') or soup.find('table', class_='results')
        if not table:
            self.logger.warning("Results table not found")
            return []

        # Parse rows (skip header)
        rows = table.find_all('tr')[1:]

        for row in rows[:max_results]:
            try:
                cells = row.find_all('td')
                if len(cells) < 3:
                    continue

                # Column structure (typical DocQNet layout):
                # cells[0] = Franchise Name / Legal Name
                # cells[1] = Document Type (FDD, Blackline, Application, etc.)
                # cells[2] = Filing Date
                # cells[N] = Details/Download link

                franchise_name = cells[0].get_text(strip=True)
                document_type = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                filing_date = cells[2].get_text(strip=True) if len(cells) > 2 else ""

                # Extract year from filing date
                fdd_year = self._extract_year(filing_date)

                # Find PDF link
                pdf_url = self._extract_pdf_url(row, cells)

                # Only include if we have valid data
                if not franchise_name:
                    continue

                fdd = {
                    "franchise_name": franchise_name,
                    "document_type": document_type,
                    "filing_date": filing_date,
                    "fdd_year": fdd_year,
                    "pdf_url": pdf_url,
                    "source_url": self.BASE_URL,
                }

                results.append(fdd)
                self.logger.debug(f"Parsed: {franchise_name} ({document_type}, {fdd_year})")

            except Exception as e:
                self.logger.warning(f"Failed to parse row: {e}")
                continue

        return results

    def _filter_fdd_documents(self, results: List[Dict]) -> List[Dict]:
        """
        Filter results to only include FDD documents.

        California returns many document types (Blackline, Application, Amendment, etc.).
        We only want actual FDDs.
        """
        filtered = []
        for fdd in results:
            doc_type = fdd.get("document_type", "").lower()

            # Skip non-FDD document types
            if any(non_fdd in doc_type for non_fdd in NON_FDD_DOCUMENT_TYPES):
                self.logger.debug(f"Filtered out: {fdd['franchise_name']} ({doc_type})")
                continue

            # Include if it's explicitly FDD
            if any(token in doc_type for token in FDD_DOCUMENT_TYPES):
                fdd["document_type"] = "FDD"
                filtered.append(fdd)
                continue

            # If no document type specified, include by default
            if not doc_type:
                fdd["document_type"] = "FDD"
                filtered.append(fdd)

        return filtered

    def _extract_pdf_url(self, row, cells) -> str:
        """Extract PDF URL from row"""
        # Try to find link in any cell
        for cell in cells:
            link = cell.find('a', href=True)
            if link and ('.pdf' in link['href'].lower() or 'document' in link['href'].lower()):
                url = link['href']
                if not url.startswith('http'):
                    url = f"https://docqnet.dfpi.ca.gov{url}"
                return url

        return None

    def _extract_year(self, text: str) -> int:
        """Extract year from text (e.g., '2024-03-15' or '03/15/2024')"""
        if not text:
            return 0

        import re
        match = re.search(r'\b(20\d{2})\b', text)
        if match:
            return int(match.group(1))

        return 0

    def _save_debug_artifacts(self, driver, suffix: str):
        """Save screenshot and HTML for debugging"""
        try:
            debug_dir = Path("outputs/debug")
            debug_dir.mkdir(parents=True, exist_ok=True)

            # Screenshot
            screenshot_path = debug_dir / f"california_{suffix}.png"
            driver.save_screenshot(str(screenshot_path))
            self.logger.debug(f"Screenshot saved: {screenshot_path}")

            # HTML
            html_path = debug_dir / f"california_{suffix}.html"
            html_path.write_text(driver.page_source)
            self.logger.debug(f"HTML saved: {html_path}")

        except Exception as e:
            self.logger.warning(f"Could not save debug artifacts: {e}")
