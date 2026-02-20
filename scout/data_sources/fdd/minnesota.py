"""Minnesota CARDS FDD Scraper - Refactored

Inherits from FDDScraperBase to eliminate code duplication.
Only contains Minnesota-specific form filling and parsing logic.
"""

import time
from typing import Dict, List
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

from data_sources.fdd.base import FDDScraperBase
from data_sources.shared.config import ScraperConfig


class MinnesotaFDDScraper(FDDScraperBase):
    """Scrape FDD documents from Minnesota CARDS database"""

    BASE_URL = "https://www.cards.commerce.state.mn.us/"
    SOURCE_ID = "minnesota_cards"

    def _scrape_fdds(self, industry: str, max_results: int, **kwargs) -> List[Dict]:
        """
        Minnesota-specific scraping logic.

        Only handles:
        - Navigating to MN CARDS site
        - Filling search form
        - Parsing results table

        All Selenium setup, PDF download handled by base class.
        """
        driver = None
        results = []

        try:
            # Create driver (from base class)
            driver = self._create_driver()

            # Navigate to franchise registrations
            search_url = f"{self.BASE_URL}franchise-registrations"
            self.logger.info(f"Navigating to: {search_url}")
            driver.get(search_url)

            time.sleep(ScraperConfig.PAGE_LOAD_WAIT)

            # Find search form
            try:
                franchise_name_input = driver.find_element(By.ID, "franchiseName")
                self.logger.debug("Search form found")
            except NoSuchElementException:
                self.logger.warning("Search form not found - page may have changed")
                self._save_debug_artifacts(driver, "form_not_found")
                return []

            # Fill search form
            self.logger.debug(f"Searching for: {industry}")
            franchise_name_input.clear()
            franchise_name_input.send_keys(industry)

            # Submit search
            search_button = driver.find_element(By.ID, "searchButton")
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
        Parse Minnesota CARDS results table.

        Args:
            soup: BeautifulSoup object of results page
            max_results: Maximum results to return

        Returns:
            List of FDD dicts
        """
        results = []

        # Find results table
        table = soup.find('table', {'id': 'resultsTable'})
        if not table:
            self.logger.warning("Results table not found")
            return []

        # Parse rows
        rows = table.find_all('tr')[1:]  # Skip header row

        for row in rows[:max_results]:
            try:
                cells = row.find_all('td')
                if len(cells) < 3:
                    continue

                # Extract data from cells
                franchise_name = cells[0].get_text(strip=True)
                fdd_year = self._extract_year(cells[1].get_text(strip=True))

                # Find PDF link
                pdf_link = cells[2].find('a', href=True)
                pdf_url = None
                if pdf_link:
                    pdf_url = pdf_link['href']
                    if not pdf_url.startswith('http'):
                        pdf_url = f"{self.BASE_URL}{pdf_url.lstrip('/')}"

                fdd = {
                    "franchise_name": franchise_name,
                    "fdd_year": fdd_year,
                    "pdf_url": pdf_url,
                    "source_url": self.BASE_URL,
                }

                results.append(fdd)
                self.logger.debug(f"Parsed: {franchise_name} ({fdd_year})")

            except Exception as e:
                self.logger.warning(f"Failed to parse row: {e}")
                continue

        return results

    def _extract_year(self, text: str) -> int:
        """Extract year from text (e.g., '2024', 'Filed: 2024')"""
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
            screenshot_path = debug_dir / f"minnesota_{suffix}.png"
            driver.save_screenshot(str(screenshot_path))
            self.logger.debug(f"Screenshot saved: {screenshot_path}")

            # HTML
            html_path = debug_dir / f"minnesota_{suffix}.html"
            html_path.write_text(driver.page_source)
            self.logger.debug(f"HTML saved: {html_path}")

        except Exception as e:
            self.logger.warning(f"Could not save debug artifacts: {e}")
