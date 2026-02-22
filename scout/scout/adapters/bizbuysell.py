"""BizBuySell adapter bridging the marketplace provider to the Scout UI."""

from typing import List

from data_sources.marketplaces.base import ListingQuery
from data_sources.marketplaces.pipeline import FetchPipeline
from data_sources.marketplaces.bizbuysell import BizBuySellProvider
from data_sources.marketplaces.store import ListingStore
from scout.domain.listing import Listing


class BizBuySellAdapter:
    """Adapter for the Scout application to fetch BizBuySell listings."""

    def __init__(self, store: ListingStore = None):
        self._store = store or ListingStore()
        self._provider = BizBuySellProvider()
        self._pipeline = FetchPipeline(
            store=self._store,
            providers=[self._provider],
        )

    def search(
        self,
        industry: str,
        location: str = "",
        max_results: int = 20,
        use_cache: bool = True,
    ) -> List[Listing]:
        """Search for listings via the FetchPipeline.

        Returns a list of Listing domain objects.
        """
        try:
            return self._pipeline.run(
                industry=industry,
                location=location,
                max_results=max_results,
                use_cache=use_cache,
            )
        except Exception:
            return []
