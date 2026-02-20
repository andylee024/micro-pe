"""Use-case: research a market with multiple data sources."""

from typing import List
from scout.domain.models import ResearchResult, MarketSummary, Business, Benchmark
from scout.adapters.maps import GoogleMapsAdapter
from scout.adapters.bizbuysell import BizBuySellAdapter
from scout.adapters.reddit import RedditSearchAdapter
from scout.application.benchmarking import compute_benchmarks_from_listings


class ResearchMarket:
    def __init__(self):
        self.maps = GoogleMapsAdapter()
        self.bizbuysell = BizBuySellAdapter()
        self.reddit = RedditSearchAdapter()

    def run(
        self,
        industry: str,
        location: str,
        max_results: int = 500,
        use_cache: bool = True,
        include_benchmarks: bool = True,
        include_reddit: bool = True,
    ) -> ResearchResult:
        businesses: List[Business] = self.maps.search(
            industry=industry,
            location=location,
            max_results=max_results,
            use_cache=use_cache,
        )

        benchmarks: List[Benchmark] = []
        if include_benchmarks:
            listings = self.bizbuysell.search(industry=industry, max_results=20, use_cache=use_cache)
            benchmark = compute_benchmarks_from_listings(industry, listings)
            if benchmark:
                benchmarks.append(benchmark)
                self._apply_benchmark_estimates(businesses, benchmark)

        summary = MarketSummary(
            industry=industry,
            location=location,
            total_businesses=len(businesses),
            benchmarks=benchmarks,
        )
        pulse = {}
        if include_reddit:
            pulse = {"reddit": self.reddit.search(f"{industry} business", limit=25)}

        return ResearchResult(summary=summary, businesses=businesses, pulse=pulse)

    def _apply_benchmark_estimates(self, businesses: List[Business], benchmark: Benchmark) -> None:
        for biz in businesses:
            biz.estimated_revenue = benchmark.median_revenue
            biz.estimated_cash_flow = benchmark.median_cash_flow
            if benchmark.median_cash_flow and benchmark.median_multiple:
                biz.estimated_value = benchmark.median_cash_flow * benchmark.median_multiple
