"""FetchPipeline: orchestrates scraping, validation, and storage."""

import logging
from typing import List, Optional

from data_sources.marketplaces.base import ListingQuery, MarketplaceProvider
from data_sources.marketplaces.store import ListingStore
from data_sources.marketplaces.validation import validate_batch
from scout.domain.listing import Listing

logger = logging.getLogger(__name__)


class FetchPipeline:
    """Orchestrates marketplace scraping with caching, validation, and storage.

    Flow: check staleness -> scrape if needed -> validate -> upsert -> return from store.
    """

    def __init__(
        self,
        store: Optional[ListingStore] = None,
        providers: Optional[List[MarketplaceProvider]] = None,
    ):
        self.store = store or ListingStore()
        self.providers = providers or []

    def run(
        self,
        industry: str,
        location: str = "",
        max_results: int = 50,
        use_cache: bool = True,
        force_refresh: bool = False,
        max_age_hours: int = 24,
    ) -> List[Listing]:
        """Run the fetch pipeline for a given industry and location.

        Args:
            industry: Industry to search (e.g. "hvac", "plumbing").
            location: Optional location filter (e.g. "texas", "TX").
            max_results: Maximum listings to return.
            use_cache: Whether to check the store for cached data.
            force_refresh: Force re-scrape even if data is fresh.
            max_age_hours: Max age in hours before data is considered stale.

        Returns:
            List of Listing objects matching the query.
        """
        all_listings: List[Listing] = []

        for provider in self.providers:
            source_id = provider.SOURCE_ID

            # Check staleness unless force_refresh
            needs_scrape = force_refresh
            if not needs_scrape and use_cache:
                if self.store.is_stale(source_id, industry, location, max_age_hours):
                    needs_scrape = True
            elif not use_cache:
                needs_scrape = True

            if needs_scrape:
                logger.info(
                    f"Scraping {source_id} for {industry}"
                    + (f" in {location}" if location else "")
                )
                query = ListingQuery(
                    industry=industry,
                    location=location,
                    max_results=max_results,
                )

                try:
                    provider_use_cache = use_cache and not force_refresh
                    listings = provider.search(query, use_cache=provider_use_cache)

                    # Validate
                    report = validate_batch(listings, industry)
                    logger.info(
                        f"Validation: {report.relevant}/{report.total} relevant "
                        f"({report.precision_pct}% precision)"
                    )

                    # Upsert into store
                    if listings:
                        count = self.store.upsert(listings)
                        logger.info(f"Upserted {count} listings into store")

                    # Log the scrape
                    self.store.log_scrape(
                        source=source_id,
                        industry=industry,
                        location=location,
                        count=len(listings),
                        status="success",
                        precision_pct=report.precision_pct,
                    )

                except Exception as e:
                    logger.error(f"Scrape failed for {source_id}: {e}")
                    self.store.log_scrape(
                        source=source_id,
                        industry=industry,
                        location=location,
                        count=0,
                        status="error",
                        error_msg=str(e),
                    )

        # Return from store (includes data from all providers and previous scrapes)
        state = ""
        if location:
            loc = location.strip().upper()
            if len(loc) == 2:
                state = loc

        results = self.store.search(
            industry=industry,
            location=location if not state else "",
            state=state,
            limit=max_results,
        )

        return results
