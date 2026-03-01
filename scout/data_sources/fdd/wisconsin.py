"""Wisconsin FDD Scraper - Refactored

Inherits from FDDScraperBase to eliminate code duplication.
Only contains Wisconsin-specific form filling and parsing logic.
"""

import time
from typing import Dict, List
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

from data_sources.fdd.base import FDDScraperBase
from data_sources.shared.config import ScraperConfig


class WisconsinFDDScraper(FDDScraperBase):
    """Scrape FDD documents from Wisconsin DFI database"""

    BASE_URL = "https://apps.dfi.wi.gov/apps/FranchiseSearch/MainSearch.aspx"
    SOURCE_ID = "wisconsin_dfi"

    def _scrape_fdds(self, industry: str, max_results: int, **kwargs) -> List[Dict]:
        """
        Wisconsin-specific scraping logic.

        Only handles:
        - Navigating to Wisconsin DFI site
        - Filling search form
        - Parsing results table

        All Selenium setup, PDF download handled by base class.
        """
        driver = None
        results = []

        try:
            # Create driver (from base class)
            driver = self._create_driver()

            # Navigate to Wisconsin DFI search
            self.logger.info(f"Navigating to: {self.BASE_URL}")
            driver.get(self.BASE_URL)
            time.sleep(ScraperConfig.PAGE_LOAD_WAIT)

            # Wait for search form
            try:
                wait = WebDriverWait(driver, ScraperConfig.DEFAULT_WAIT_SECONDS)
                search_input = wait.until(
                    EC.presence_of_element_located((By.ID, "txtName"))
                )
                self.logger.debug("Search form found")
            except Exception:
                self.logger.warning("Search form not found - page may have changed")
                self._save_debug_artifacts(driver, "form_not_found")
                return []

            # Fill search form
            self.logger.debug(f"Searching for: {industry}")
            search_input.clear()
            search_input.send_keys(industry)

            # Submit search
            search_button = driver.find_element(By.ID, "btnSearch")
            search_button.click()

            # Wait for results
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

    def _parse_results_table(self, soup: BeautifulSoup, max_results: int) -> List[Dict]:
        """
        Parse Wisconsin DFI results table.

        Args:
            soup: BeautifulSoup object of results page
            max_results: Maximum results to return

        Returns:
            List of FDD dicts
        """
        results = []

        # Find results table (id='grdSearchResults')
        table = soup.find('table', id='grdSearchResults')
        if not table:
            self.logger.warning("Results table not found")
            return []

        # Find all result rows (odd/even rows)
        odd_rows = table.find_all('tr', class_='SearchResultsOddRow')
        even_rows = table.find_all('tr', class_='SearchResultsEvenRow')
        all_rows = odd_rows + even_rows

        # Sort by document order
        all_rows = sorted(
            all_rows,
            key=lambda row: int(row.find_all('td')[0].get_text(strip=True)) if row.find_all('td') else 0,
            reverse=True
        )

        for row in all_rows[:max_results]:
            try:
                cells = row.find_all('td')
                if len(cells) < 7:
                    continue

                # Column structure:
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
                fdd_year = self._extract_year(effective_date)

                # Extract details URL (leads to page with FDD PDF)
                details_link = cells[6].find('a')
                pdf_url = None
                if details_link and details_link.get('href'):
                    pdf_url = details_link['href']
                    # Make absolute URL
                    if not pdf_url.startswith('http'):
                        pdf_url = f"https://apps.dfi.wi.gov/apps/FranchiseSearch/{pdf_url}"

                # Only include records with valid details URL
                if not pdf_url:
                    continue

                fdd = {
                    "franchise_name": franchise_name,
                    "legal_name": legal_name,
                    "trade_name": trade_name,
                    "document_id": file_number,
                    "effective_date": effective_date,
                    "status": status,
                    "pdf_url": pdf_url,
                    "fdd_year": fdd_year,
                    "source_url": self.BASE_URL,
                }

                results.append(fdd)
                self.logger.debug(f"Parsed: {franchise_name} ({fdd_year})")

            except Exception as e:
                self.logger.warning(f"Failed to parse row: {e}")
                continue

        return results

    def _extract_year(self, date_str: str) -> int:
        """Extract year from date string (e.g., '4/30/2025' → 2025)"""
        if not date_str or '/' not in date_str:
            return 0

        try:
            return int(date_str.split('/')[-1])
        except (ValueError, IndexError):
            return 0

    def _save_debug_artifacts(self, driver, suffix: str):
        """Save screenshot and HTML for debugging"""
        try:
            debug_dir = Path("outputs/debug")
            debug_dir.mkdir(parents=True, exist_ok=True)

            # Screenshot
            screenshot_path = debug_dir / f"wisconsin_{suffix}.png"
            driver.save_screenshot(str(screenshot_path))
            self.logger.debug(f"Screenshot saved: {screenshot_path}")

            # HTML
            html_path = debug_dir / f"wisconsin_{suffix}.html"
            html_path.write_text(driver.page_source)
            self.logger.debug(f"HTML saved: {html_path}")

        except Exception as e:
            self.logger.warning(f"Could not save debug artifacts: {e}")
