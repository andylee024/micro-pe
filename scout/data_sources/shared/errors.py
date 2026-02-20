"""Custom exceptions for Scout scrapers"""


class ScoutError(Exception):
    """Base exception for all Scout errors"""
    pass


class ScraperError(ScoutError):
    """Base exception for scraper errors"""
    pass


class SeleniumSetupError(ScraperError):
    """Failed to setup Selenium driver"""
    pass


class FormNotFoundError(ScraperError):
    """Search form not found on page"""
    def __init__(self, form_id: str, url: str):
        self.form_id = form_id
        self.url = url
        super().__init__(f"Form '{form_id}' not found at {url}")


class NoResultsError(ScraperError):
    """Search returned no results (this is not always an error)"""
    def __init__(self, industry: str):
        self.industry = industry
        super().__init__(f"No results found for '{industry}'")


class PDFDownloadError(ScraperError):
    """Failed to download PDF"""
    def __init__(self, url: str, reason: str):
        self.url = url
        self.reason = reason
        super().__init__(f"Failed to download PDF from {url}: {reason}")


class CacheError(ScoutError):
    """Cache operation failed"""
    pass


class APIError(ScoutError):
    """External API error"""
    def __init__(self, service: str, status_code: int, message: str):
        self.service = service
        self.status_code = status_code
        super().__init__(f"{service} API error ({status_code}): {message}")


class RateLimitError(APIError):
    """API rate limit exceeded"""
    def __init__(self, service: str, retry_after: int = None):
        self.retry_after = retry_after
        msg = f"Rate limited"
        if retry_after:
            msg += f" (retry after {retry_after}s)"
        super().__init__(service, 429, msg)
