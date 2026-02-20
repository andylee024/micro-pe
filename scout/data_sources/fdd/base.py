"""Base class for all FDD scrapers with shared Selenium and PDF download logic"""

import time
import random
from abc import abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

import httpx
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from data_sources.shared.base import Tool
from data_sources.shared.config import ScraperConfig
from data_sources.shared.errors import SeleniumSetupError, PDFDownloadError


class FDDScraperBase(Tool):
    """
    Base class for all FDD scrapers.

    Provides:
    - Shared Selenium setup with anti-detection
    - Shared PDF download logic
    - Standardized search() template method
    - Consistent caching and logging

    Subclasses only need to implement:
    - _scrape_fdds(): State-specific form filling and parsing
    """

    # Subclasses should override these
    BASE_URL: str = ""
    SOURCE_ID: str = ""  # Optional: override source identifier (e.g., "wisconsin_dfi")
    CACHE_TTL_DAYS = ScraperConfig.FDD_CACHE_TTL_DAYS

    def __init__(self, **kwargs):
        """Initialize FDD scraper with output directories"""
        super().__init__(**kwargs)
        self.output_dir = Path(ScraperConfig.FDD_OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ==================== TEMPLATE METHOD ====================

    def search(
        self,
        industry: str,
        max_results: int = 10,
        download_pdfs: bool = False,
        use_cache: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Template method for FDD search.

        Pattern:
        1. Check cache (shared)
        2. Call _scrape_fdds() (state-specific - delegates to subclass)
        3. Download PDFs if requested (shared)
        4. Build response (shared)
        5. Save to cache (shared)

        Args:
            industry: Search keyword
            max_results: Maximum results to return
            download_pdfs: Whether to download PDF files
            use_cache: Whether to use cached results
            **kwargs: State-specific parameters

        Returns:
            Standardized response dict
        """
        self.logger.info(f"Searching for '{industry}' (max: {max_results})")

        # 1. Check cache
        cache_key = self._get_cache_key(industry, max_results, **kwargs)
        if use_cache:
            cached = self.load_cache(cache_key)
            if cached:
                return cached["data"]

        # 2. Scrape (delegates to subclass)
        self.logger.info(f"Connecting to {self.BASE_URL}")
        results = self._scrape_fdds(industry, max_results, **kwargs)

        if not results:
            self.logger.warning(f"No results found for '{industry}'")
            response = self._build_response(industry, [], **kwargs)
            if use_cache:
                self.save_cache(cache_key, response, self.CACHE_TTL_DAYS)
            return response

        self.logger.info(f"Found {len(results)} FDDs")

        # 3. Download PDFs if requested
        if download_pdfs:
            self._download_all_pdfs(results)

        # 4. Build response
        response = self._build_response(industry, results, **kwargs)

        # 5. Cache
        if use_cache:
            self.save_cache(cache_key, response, self.CACHE_TTL_DAYS)

        return response

    @abstractmethod
    def _scrape_fdds(self, industry: str, max_results: int, **kwargs) -> List[Dict]:
        """
        State-specific scraping logic.

        MUST BE IMPLEMENTED BY SUBCLASS.

        This is where you fill forms, parse HTML, extract FDD data.
        Use self._create_driver() to get a configured Selenium driver.

        Args:
            industry: Search keyword
            max_results: Maximum results
            **kwargs: State-specific parameters

        Returns:
            List of FDD dicts with at least:
            - franchise_name: str
            - pdf_url: str (optional)
            - fdd_year: int (optional)
        """
        pass

    # ==================== SHARED SELENIUM SETUP ====================

    def _create_driver(self) -> webdriver.Chrome:
        """
        Create Chrome driver with anti-detection.

        Returns:
            Configured Chrome WebDriver

        Raises:
            SeleniumSetupError: If driver creation fails
        """
        try:
            options = self._get_chrome_options()
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

            # Apply anti-detection measures
            self._apply_anti_detection(driver)

            self.logger.debug("Chrome driver created successfully")
            return driver

        except Exception as e:
            self.logger.error(f"Failed to create Chrome driver: {e}")
            raise SeleniumSetupError(f"Could not create driver: {e}")

    def _get_chrome_options(self) -> Options:
        """
        Get Chrome options with anti-detection.

        Returns:
            Chrome Options object
        """
        options = Options()

        # Basic options
        if ScraperConfig.CHROME_HEADLESS:
            options.add_argument('--headless=new')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Anti-detection
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # User agent
        options.add_argument(f'--user-agent={ScraperConfig.CHROME_USER_AGENT}')

        # Additional stealth
        options.add_argument('--disable-extensions')
        options.add_argument('--profile-directory=Default')
        options.add_argument('--disable-plugins-discovery')

        return options

    def _apply_anti_detection(self, driver: webdriver.Chrome):
        """
        Apply CDP anti-detection measures.

        Args:
            driver: Chrome WebDriver instance
        """
        try:
            # Override user agent via CDP
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": ScraperConfig.CHROME_USER_AGENT
            })

            # Hide webdriver property
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            self.logger.debug("Applied anti-detection measures")

        except Exception as e:
            self.logger.warning(f"Could not apply anti-detection: {e}")
            # Continue anyway - not critical

    # ==================== SHARED PDF DOWNLOAD ====================

    def _download_all_pdfs(self, results: List[Dict]):
        """
        Download PDFs for all results.

        Args:
            results: List of FDD dicts with 'pdf_url' field
        """
        self.logger.info(f"Downloading PDFs for {len(results)} FDDs")

        for i, fdd in enumerate(results, 1):
            pdf_url = fdd.get("pdf_url")
            if not pdf_url:
                self.logger.debug(f"[{i}/{len(results)}] {fdd.get('franchise_name')}: No PDF URL")
                continue

            self.logger.info(f"[{i}/{len(results)}] Downloading: {fdd.get('franchise_name')}")

            try:
                self._download_pdf(fdd, pdf_url)
                self.logger.info(f"  ✓ Downloaded ({fdd.get('pdf_size_mb', 0):.1f} MB)")

                # Rate limiting between downloads
                time.sleep(random.uniform(
                    ScraperConfig.RATE_LIMIT_DELAY_MIN,
                    ScraperConfig.RATE_LIMIT_DELAY_MAX
                ))

            except PDFDownloadError as e:
                self.logger.error(f"  ✗ Download failed: {e.reason}")
                fdd['pdf_download_error'] = e.reason

            except Exception as e:
                self.logger.error(f"  ✗ Unexpected error: {e}")
                fdd['pdf_download_error'] = str(e)

    def _download_pdf(self, fdd: Dict, pdf_url: str):
        """
        Download single PDF file.

        Args:
            fdd: FDD dict to update with pdf_path
            pdf_url: URL to download from

        Raises:
            PDFDownloadError: If download fails
        """
        try:
            # Generate safe filename
            franchise_name = fdd.get("franchise_name", "unknown")
            safe_name = "".join(c for c in franchise_name if c.isalnum() or c in (' ', '-', '_'))
            safe_name = safe_name.replace(' ', '_')[:50]  # Limit length

            fdd_year = fdd.get("fdd_year", "unknown")
            filename = f"{safe_name}_{fdd_year}.pdf"
            pdf_path = self.output_dir / filename

            # Download with httpx
            response = httpx.get(
                pdf_url,
                timeout=ScraperConfig.PDF_DOWNLOAD_TIMEOUT,
                follow_redirects=True
            )

            if response.status_code != 200:
                raise PDFDownloadError(
                    pdf_url,
                    f"HTTP {response.status_code}"
                )

            # Check size
            content_length = len(response.content)
            size_mb = content_length / (1024 * 1024)

            if size_mb > ScraperConfig.PDF_MAX_SIZE_MB:
                raise PDFDownloadError(
                    pdf_url,
                    f"PDF too large ({size_mb:.1f} MB > {ScraperConfig.PDF_MAX_SIZE_MB} MB)"
                )

            # Save
            pdf_path.write_bytes(response.content)

            # Update FDD dict
            fdd['pdf_path'] = str(pdf_path)
            fdd['pdf_size_mb'] = round(size_mb, 2)
            fdd['pdf_downloaded'] = True

            self.logger.debug(f"Saved PDF: {pdf_path}")

        except httpx.TimeoutException:
            raise PDFDownloadError(pdf_url, "Download timeout")
        except httpx.HTTPError as e:
            raise PDFDownloadError(pdf_url, f"HTTP error: {e}")
        except Exception as e:
            raise PDFDownloadError(pdf_url, str(e))

    # ==================== UTILITIES ====================

    def _get_cache_key(self, industry: str, max_results: int, **kwargs) -> str:
        """
        Generate cache key from search parameters.

        Args:
            industry: Search keyword
            max_results: Max results
            **kwargs: Additional parameters to include in key

        Returns:
            Cache key string
        """
        # Base key
        key = f"fdd_{industry.replace(' ', '_')}_{max_results}"

        # Add any state-specific parameters
        for k, v in sorted(kwargs.items()):
            if v is not None:
                key += f"_{k}_{v}"

        return key

    def _get_cache_path(self, cache_key: str) -> Path:
        """
        Get the cache file path for a given key.

        Args:
            cache_key: Unique cache identifier

        Returns:
            Path to cache file
        """
        return self.cache_dir / f"{cache_key}.json"

    def _build_response(self, industry: str, results: List[Dict], **kwargs) -> Dict[str, Any]:
        """
        Build standardized response dict.

        Args:
            industry: Search keyword
            results: List of FDD dicts
            **kwargs: Additional fields to include

        Returns:
            Standardized response dict
        """
        # Use SOURCE_ID if set, otherwise derive from class name
        source_id = self.SOURCE_ID if self.SOURCE_ID else self.__class__.__name__.lower().replace("scraper", "").replace("fdd", "")

        response = {
            "source": source_id,
            "search_date": datetime.now().isoformat(),
            "industry": industry,
            "total_found": len(results),
            "results": results
        }

        # Add any state-specific fields
        response.update(kwargs)

        return response
