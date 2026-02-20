"""NASAA FRED (Electronic Filing Depository) FDD Scraper - Refactored

Inherits from FDDScraperBase to eliminate code duplication.
Only contains NASAA-specific form filling, parsing, and multi-state tracking logic.

Covers 7 states: NY, IL, MD, VA, WA, ND, RI.
"""

import time
import re
from typing import Dict, List, Optional
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

from data_sources.fdd.base import FDDScraperBase
from data_sources.shared.config import ScraperConfig


class NASAAFredScraper(FDDScraperBase):
    """Scrape FDD documents from NASAA Electronic Filing Depository (7-state database)"""

    BASE_URL = "https://www.nasaaefd.org/Franchise/Search"
    SOURCE_ID = "nasaa_fred"
    STATES = ["NY", "IL", "MD", "VA", "WA", "ND", "RI"]

    def search(
        self,
        industry: str,
        max_results: int = 10,
        states: Optional[List[str]] = None,
        download_pdfs: bool = False,
        use_cache: bool = True,
        **kwargs
    ) -> Dict:
        """
        Search for FDDs with optional state filtering.

        Args:
            industry: Search keyword
            max_results: Max results to return
            states: Optional list of state codes to filter (e.g., ["NY", "IL"])
            download_pdfs: Whether to download PDFs
            use_cache: Whether to use cache

        Returns:
            Standardized response dict with state-filtered results
        """
        # Normalize state filter
        states_filter = [s.upper() for s in states] if states else None

        if states_filter:
            self.logger.info(f"Filtering to states: {states_filter}")

        # Use base class search, but override cache key for state filtering
        if states_filter:
            kwargs['states'] = '_'.join(sorted(states_filter))

        # Call base class search
        response = super().search(
            industry=industry,
            max_results=max_results,
            download_pdfs=download_pdfs,
            use_cache=use_cache,
            **kwargs
        )

        # Apply state filtering to results
        if states_filter and response.get('results'):
            original_count = len(response['results'])
            response['results'] = [
                r for r in response['results']
                if r.get("filing_state", "").upper() in states_filter
            ]
            response['total_found'] = len(response['results'])
            self.logger.info(f"After state filter: {len(response['results'])} of {original_count}")

        # Add state metadata
        response['states_searched'] = self.STATES
        if states_filter:
            response['states_filtered'] = states_filter

        return response

    def _scrape_fdds(self, industry: str, max_results: int, **kwargs) -> List[Dict]:
        """
        NASAA FRED-specific scraping logic.

        Only handles:
        - Navigating to NASAA EFD site
        - Filling search form (with multiple fallback selectors)
        - Parsing results table
        - Extracting filing state for each FDD

        All Selenium setup, PDF download handled by base class.
        """
        driver = None
        results = []

        try:
            # Create driver (from base class)
            driver = self._create_driver()

            # Navigate to NASAA EFD
            self.logger.info(f"Navigating to: {self.BASE_URL}")
            driver.get(self.BASE_URL)
            time.sleep(ScraperConfig.DEFAULT_WAIT_SECONDS)

            # Find search form (NASAA uses ASP.NET with dynamic rendering)
            search_input = self._find_search_input(driver)
            if not search_input:
                self.logger.warning("Search form not found")
                self._save_debug_artifacts(driver, "form_not_found")
                return []

            # Fill search form
            self.logger.debug(f"Searching for: {industry}")
            search_input.clear()
            search_input.send_keys(industry)

            # Submit search
            submit_button = self._find_submit_button(driver)
            if not submit_button:
                self.logger.warning("Submit button not found")
                self._save_debug_artifacts(driver, "button_not_found")
                return []

            submit_button.click()
            time.sleep(ScraperConfig.FORM_SUBMIT_WAIT)

            # Parse results
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            results = self._parse_results_table(soup, max_results)

            self.logger.info(f"Parsed {len(results)} results from table")

        except Exception as e:
            self.logger.error(f"Scraping failed: {e}", exc_info=True)
            if driver:
                self._save_debug_artifacts(driver, "error")

        finally:
            if driver:
                driver.quit()

        return results

    def _find_search_input(self, driver) -> Optional[any]:
        """Find search input with multiple fallback selectors"""
        # NASAA EFD uses ASP.NET with dynamic IDs - try multiple selectors
        selectors = [
            (By.ID, "txtFranchiseName"),
            (By.ID, "FranchiseName"),
            (By.ID, "franchiseName"),
            (By.ID, "txtSearch"),
            (By.NAME, "FranchiseName"),
            (By.CSS_SELECTOR, "input[type='text'][placeholder*='ranch']"),
            (By.CSS_SELECTOR, "input[type='text'][placeholder*='earch']"),
            (By.CSS_SELECTOR, "input.form-control[type='text']"),
        ]

        for by, selector in selectors:
            try:
                element = driver.find_element(by, selector)
                self.logger.debug(f"Found search input via: {by}='{selector}'")
                return element
            except NoSuchElementException:
                continue

        # Fallback: find first visible text input
        try:
            all_text_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
            visible_inputs = [inp for inp in all_text_inputs if inp.is_displayed()]
            if visible_inputs:
                self.logger.debug("Found search input via fallback (first visible)")
                return visible_inputs[0]
        except Exception:
            pass

        return None

    def _find_submit_button(self, driver) -> Optional[any]:
        """Find submit button with multiple fallback selectors"""
        selectors = [
            (By.ID, "btnSearch"),
            (By.ID, "searchButton"),
            (By.ID, "MainContent_btnSearch"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.CSS_SELECTOR, "input[type='submit']"),
            (By.CSS_SELECTOR, "button.btn-primary"),
            (By.XPATH, "//button[contains(text(), 'Search')]"),
            (By.XPATH, "//input[@value='Search']"),
        ]

        for by, selector in selectors:
            try:
                element = driver.find_element(by, selector)
                self.logger.debug(f"Found submit button via: {by}='{selector}'")
                return element
            except NoSuchElementException:
                continue

        return None

    def _parse_results_table(self, soup: BeautifulSoup, max_results: int) -> List[Dict]:
        """
        Parse NASAA EFD results table.

        Extracts filing_state from each row (unique to NASAA multi-state database).

        Args:
            soup: BeautifulSoup object of results page
            max_results: Maximum results to return

        Returns:
            List of FDD dicts with filing_state
        """
        results = []

        # Find results table (NASAA uses GridView or similar)
        table = soup.find('table', {'class': 'table'}) or soup.find('table', id=re.compile('grid', re.I))
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

                # Column structure (typical NASAA layout):
                # cells[0] = Franchise Name
                # cells[1] = Filing Date or Document Type
                # cells[2] = State (unique to NASAA)
                # cells[N] = Details/Download link

                franchise_name = cells[0].get_text(strip=True)
                filing_date_text = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                filing_state = cells[2].get_text(strip=True) if len(cells) > 2 else ""

                # Extract year from filing date
                fdd_year = self._extract_year(filing_date_text)

                # Find PDF link (usually last column or link in franchise name cell)
                pdf_url = self._extract_pdf_url(row, cells)

                # Only include if we have valid data
                if not franchise_name:
                    continue

                fdd = {
                    "franchise_name": franchise_name,
                    "filing_date": filing_date_text,
                    "filing_state": filing_state.upper() if filing_state else "",
                    "fdd_year": fdd_year,
                    "pdf_url": pdf_url,
                    "source_url": self.BASE_URL,
                }

                results.append(fdd)
                self.logger.debug(f"Parsed: {franchise_name} ({filing_state}, {fdd_year})")

            except Exception as e:
                self.logger.warning(f"Failed to parse row: {e}")
                continue

        return results

    def _extract_pdf_url(self, row, cells) -> Optional[str]:
        """Extract PDF URL from row"""
        # Try to find link in any cell
        for cell in cells:
            link = cell.find('a', href=True)
            if link and '.pdf' in link['href'].lower():
                url = link['href']
                if not url.startswith('http'):
                    url = f"https://www.nasaaefd.org{url}"
                return url

        return None

    def _extract_year(self, text: str) -> int:
        """Extract year from text (e.g., '2024-03-15' or '03/15/2024')"""
        if not text:
            return 0

        # Try to find 4-digit year
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
            screenshot_path = debug_dir / f"nasaa_fred_{suffix}.png"
            driver.save_screenshot(str(screenshot_path))
            self.logger.debug(f"Screenshot saved: {screenshot_path}")

            # HTML
            html_path = debug_dir / f"nasaa_fred_{suffix}.html"
            html_path.write_text(driver.page_source)
            self.logger.debug(f"HTML saved: {html_path}")

        except Exception as e:
            self.logger.warning(f"Could not save debug artifacts: {e}")
