"""Use-case: research a market with multiple data sources."""

import statistics
from typing import List

from scout.domain.models import (
    ResearchResult,
    MarketSummary,
    Business,
    Benchmark,
    MarketOverview,
    MarketPulse,
)
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
        query: str | None = None,
        max_results: int = 500,
        use_cache: bool = True,
        include_benchmarks: bool = True,
        include_reddit: bool = True,
        on_progress=None,
    ) -> ResearchResult:
        def _progress(stage: str, status: str, count: int = 0):
            if on_progress:
                try:
                    on_progress(stage, status, count)
                except Exception:
                    pass  # never let progress callbacks crash the pipeline

        _progress("maps", "running")
        businesses: List[Business] = self.maps.search(
            industry=industry,
            location=location,
            max_results=max_results,
            use_cache=use_cache,
        )
        _progress("maps", "done", len(businesses))

        # --- BizBuySell ---
        bbs_listings: List[dict] = []
        benchmarks: List[Benchmark] = []
        if include_benchmarks:
            _progress("bizbuysell", "running")
            bizbuysell_error = False
            try:
                bbs_data = self.bizbuysell.search(industry, location, use_cache=use_cache)
                if isinstance(bbs_data, list):
                    bbs_listings = bbs_data
                elif isinstance(bbs_data, dict):
                    bbs_listings = bbs_data.get("results", bbs_data.get("listings", []))
            except Exception:
                bizbuysell_error = True  # BizBuySell unavailable — proceed without it

            if bizbuysell_error:
                _progress("bizbuysell", "error")
            else:
                benchmark = compute_benchmarks_from_listings(industry, bbs_listings)
                if benchmark:
                    benchmarks.append(benchmark)
                    self._apply_benchmark_estimates(businesses, benchmark)
                _progress("bizbuysell", "done", len(bbs_listings))
        else:
            _progress("bizbuysell", "done")

        # Apply per-business financial estimates using benchmark signals
        from scout.application.estimate_financials import estimate_business_financials
        benchmark_for_estimates = benchmarks[0] if benchmarks else None
        businesses = [
            estimate_business_financials(b, benchmark_for_estimates) for b in businesses
        ]

        summary = MarketSummary(
            industry=industry,
            location=location,
            total_businesses=len(businesses),
            query=query or f"{industry} businesses in {location}",
            benchmarks=benchmarks,
        )

        # --- Reddit + AI synthesis ---
        pulse: MarketPulse = MarketPulse()
        if include_reddit:
            _progress("reddit", "running")
            reddit_error = False
            reddit_data = {"thread_count": 0, "reddit_threads": []}
            try:
                reddit_data = self.reddit.search(industry, location, use_cache=use_cache)
            except Exception:
                reddit_error = True

            if reddit_error:
                _progress("reddit", "error")
                _progress("ai_analysis", "error")
                pulse = MarketPulse()
            else:
                _progress("reddit", "done", reddit_data.get("thread_count", 0))
                # AI analysis stage
                _progress("ai_analysis", "running")
                pulse = self._synthesize_pulse_from_reddit(reddit_data, industry)
                _progress("ai_analysis", "done")
        else:
            _progress("reddit", "done")
            _progress("ai_analysis", "done")

        market_overview = self._compute_market_overview(businesses, bbs_listings, industry)

        return ResearchResult(
            summary=summary,
            businesses=businesses,
            pulse=pulse,
            market_overview=market_overview,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _apply_benchmark_estimates(
        self, businesses: List[Business], benchmark: Benchmark
    ) -> None:
        """Apply flat benchmark values to businesses that lack estimates."""
        for biz in businesses:
            if biz.estimated_revenue is None:
                biz.estimated_revenue = benchmark.median_revenue
            if biz.estimated_cash_flow is None:
                biz.estimated_cash_flow = benchmark.median_cash_flow
            if (
                biz.estimated_value is None
                and benchmark.median_cash_flow
                and benchmark.median_multiple
            ):
                biz.estimated_value = benchmark.median_cash_flow * benchmark.median_multiple

    def _synthesize_pulse_from_reddit(
        self, reddit_data: dict, industry: str
    ) -> MarketPulse:
        """Use Claude to extract structured insights from Reddit threads."""
        from scout import config

        threads = reddit_data.get("reddit_threads", [])

        # Base pulse structure (used as fallback if synthesis fails)
        base_pulse = {
            "business_model": {
                "customers": "Residential + commercial",
                "revenue": "Service contracts + one-off jobs",
            },
            "operating_models": [
                "Owner-operator (solo/crew)",
                "Multi-tech local operator",
            ],
            "opportunities": [],
            "risks": [],
            "sources": {
                "reddit": reddit_data.get("thread_count", 0),
                "reddit_threads": threads,
                "reviews": 0,
                "reports": 0,
                "listings": 0,
            },
        }

        if not threads or not config.ANTHROPIC_API_KEY:
            return MarketPulse.from_dict(base_pulse)

        try:
            import anthropic
            import json

            client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

            thread_text = "\n".join(
                f"- [{t.get('sub', '')}] {t.get('title', '')}: {t.get('excerpt', '')}"
                for t in threads[:8]
            )

            prompt = f"""Analyze these Reddit threads about {industry} businesses from an acquisition perspective.

Threads:
{thread_text}

Extract and respond with ONLY valid JSON in this exact format:
{{
  "opportunities": ["opportunity 1 sentence", "opportunity 2 sentence", "opportunity 3 sentence"],
  "risks": ["risk 1 sentence", "risk 2 sentence", "risk 3 sentence"],
  "business_model": {{
    "customers": "brief description of customer types",
    "revenue": "brief description of revenue streams"
  }},
  "operating_models": ["model 1", "model 2", "model 3", "model 4"]
}}

Keep each item to 1 sentence. Be specific to {industry}."""

            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}],
            )

            raw = response.content[0].text.strip()
            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            parsed = json.loads(raw.strip())

            base_pulse.update(
                {
                    "business_model": parsed.get(
                        "business_model", base_pulse["business_model"]
                    ),
                    "operating_models": parsed.get(
                        "operating_models", base_pulse["operating_models"]
                    ),
                    "opportunities": parsed.get("opportunities", []),
                    "risks": parsed.get("risks", []),
                }
            )

        except Exception:
            pass  # Fall back to base_pulse on any error

        return MarketPulse.from_dict(base_pulse)

    def _compute_market_overview(
        self, businesses: List[Business], bbs_listings: list, industry: str
    ) -> MarketOverview:
        """Build market_overview dict from BizBuySell listings and business data."""

        # Compute quality from businesses
        ratings = [b.rating for b in businesses if b.rating is not None]
        total_reviews = sum(b.reviews or 0 for b in businesses)
        avg_rating = round(statistics.mean(ratings), 1) if ratings else 0.0

        # Financial defaults
        fin: dict = {
            "fdd_count": 0,
            "confidence": "low",
            "median_revenue": "—",
            "revenue_range": "",
            "ebitda_margin": "—",
            "margin_range": "",
            "typical_acquisition": "—",
        }

        bbs_source: dict = {}

        if bbs_listings:
            asking_prices: list = []
            revenues: list = []
            cash_flows: list = []
            days_listed_list: list = []

            for listing in bbs_listings:
                for key in ("asking_price", "price", "list_price"):
                    val = listing.get(key)
                    if val and isinstance(val, (int, float)) and val > 0:
                        asking_prices.append(val)
                        break
                for key in ("revenue", "gross_revenue", "annual_revenue"):
                    val = listing.get(key)
                    if val and isinstance(val, (int, float)) and val > 0:
                        revenues.append(val)
                        break
                for key in ("cash_flow", "sde", "ebitda", "net_income"):
                    val = listing.get(key)
                    if val and isinstance(val, (int, float)) and val > 0:
                        cash_flows.append(val)
                        break
                for key in ("days_on_market", "days_listed"):
                    val = listing.get(key)
                    if val and isinstance(val, (int, float)) and val > 0:
                        days_listed_list.append(val)
                        break

            def _fmt_money(v: float) -> str:
                if v >= 1_000_000:
                    return f"${v / 1_000_000:.1f}M"
                if v >= 1_000:
                    return f"${v / 1_000:.0f}K"
                return f"${v:.0f}"

            if revenues:
                med_rev = statistics.median(revenues)
                fin["median_revenue"] = _fmt_money(med_rev)
                fin["revenue_range"] = (
                    f"{_fmt_money(min(revenues))} – {_fmt_money(max(revenues))}"
                )
                fin["confidence"] = "medium" if len(revenues) >= 5 else "low"
                fin["fdd_count"] = len(revenues)

            if cash_flows and revenues:
                margins = [
                    cf / rev * 100
                    for cf, rev in zip(cash_flows, revenues)
                    if rev > 0
                ]
                if margins:
                    med_margin = statistics.median(margins)
                    fin["ebitda_margin"] = f"{med_margin:.0f}%"
                    fin["margin_range"] = f"{min(margins):.0f}–{max(margins):.0f}%"

            if asking_prices:
                fin["typical_acquisition"] = (
                    f"{_fmt_money(min(asking_prices))} – {_fmt_money(max(asking_prices))}"
                )

            bbs_source = {
                "listing_count": len(bbs_listings),
                "period": "last 90 days",
                "median_ask": (
                    _fmt_money(statistics.median(asking_prices))
                    if asking_prices
                    else "—"
                ),
                "revenue_range": fin["revenue_range"],
                "cashflow_range": (
                    f"{_fmt_money(min(cash_flows))} – {_fmt_money(max(cash_flows))}"
                    if cash_flows
                    else "—"
                ),
                "avg_days_listed": (
                    round(statistics.mean(days_listed_list))
                    if days_listed_list
                    else "—"
                ),
            }

        density = (
            "high density"
            if len(businesses) > 20
            else "medium density"
            if len(businesses) > 10
            else "low density"
        )

        market_overview = {
            "total_businesses": len(businesses),
            "market_density": density,
            "est_market_value": "",
            "financial": fin,
            "quality": {
                "avg_rating": avg_rating,
                "sentiment_positive": 0,
                "review_volume": total_reviews,
            },
            "trends": {
                "job_postings": "—",
                "new_entrants": "—",
                "search_volume": "—",
            },
            "outlook": {
                "grade": "—",
                "note": "",
            },
            "sources": {
                "fdd_filings": [],
                "bizbuysell": bbs_source,
            },
        }
        return MarketOverview.from_dict(market_overview)
