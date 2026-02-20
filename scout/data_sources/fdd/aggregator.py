"""FDD Aggregator - Unified interface to query all state FDD databases

Provides a single search interface that queries:
- Minnesota CARDS
- Wisconsin DFI
- NASAA FRED (7 states: NY, IL, MD, VA, WA, ND, RI)
- California DocQNet

Deduplicates results across states and returns combined data with state provenance.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from data_sources.fdd.minnesota import MinnesotaFDDScraper
from data_sources.fdd.wisconsin import WisconsinFDDScraper
from data_sources.fdd.nasaa_fred import NASAAFredScraper
from data_sources.fdd.california import CaliforniaFDDScraper


class FDDAggregator:
    """Aggregate FDD data from all state scrapers"""

    def __init__(self):
        """Initialize all FDD scrapers"""
        self.scrapers = {
            'minnesota': MinnesotaFDDScraper(),
            'wisconsin': WisconsinFDDScraper(),
            'nasaa_fred': NASAAFredScraper(),
            'california': CaliforniaFDDScraper()
        }

    def search_all(
        self,
        industry: str,
        max_results_per_source: int = 10,
        download_pdfs: bool = False,
        extract_item19: bool = False,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Search ALL FDD databases for an industry.

        Args:
            industry: Search keyword (e.g., "car wash", "McDonald's")
            max_results_per_source: Max results per state database
            download_pdfs: Whether to download PDFs from each source
            extract_item19: Whether to extract Item 19 financial data
            use_cache: Whether to use cached results

        Returns:
            Dict with results from all sources and deduplicated combined list
        """
        print(f"\n{'='*70}")
        print(f"FDD AGGREGATOR: Searching all sources for '{industry}'")
        print(f"{'='*70}")

        all_results = {}
        total_found = 0

        # Query each scraper
        for state_name, scraper in self.scrapers.items():
            print(f"\n[{state_name.upper()}] Querying...")
            try:
                results = scraper.search(
                    industry=industry,
                    max_results=max_results_per_source,
                    download_pdfs=download_pdfs,
                    extract_item19=extract_item19,
                    use_cache=use_cache
                )

                all_results[state_name] = results
                found = results.get('total_found', 0)
                total_found += found
                print(f"[{state_name.upper()}] ✅ Found {found} FDDs")

            except Exception as e:
                print(f"[{state_name.upper()}] ❌ Error: {e}")
                all_results[state_name] = {
                    "error": str(e),
                    "source": state_name,
                    "total_found": 0,
                    "results": []
                }

        # Deduplicate across states
        print(f"\n{'='*70}")
        print(f"DEDUPLICATION: Processing {total_found} total results")
        deduplicated = self._deduplicate(all_results)
        print(f"DEDUPLICATION: {len(deduplicated)} unique FDDs after deduplication")
        print(f"{'='*70}\n")

        # Build aggregated response
        return {
            "source": "fdd_aggregator",
            "search_date": datetime.now().isoformat(),
            "industry": industry,
            "total_states_searched": len(self.scrapers),
            "total_found_before_dedup": total_found,
            "total_unique": len(deduplicated),
            "by_state": all_results,
            "deduplicated": deduplicated
        }

    def search_by_states(
        self,
        industry: str,
        states: List[str],
        max_results_per_source: int = 10,
        download_pdfs: bool = False,
        extract_item19: bool = False,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Search specific states only.

        Args:
            industry: Search keyword
            states: List of state identifiers (e.g., ['minnesota', 'california'])
            max_results_per_source: Max results per state
            download_pdfs: Whether to download PDFs
            extract_item19: Whether to extract Item 19
            use_cache: Whether to use cache

        Returns:
            Dict with results from specified states
        """
        print(f"\n{'='*70}")
        print(f"FDD AGGREGATOR: Searching {states} for '{industry}'")
        print(f"{'='*70}")

        all_results = {}
        total_found = 0

        # Query only specified states
        for state_name in states:
            state_lower = state_name.lower()
            if state_lower not in self.scrapers:
                print(f"[{state_name.upper()}] ⚠️  Unknown state, skipping")
                continue

            scraper = self.scrapers[state_lower]
            print(f"\n[{state_name.upper()}] Querying...")

            try:
                results = scraper.search(
                    industry=industry,
                    max_results=max_results_per_source,
                    download_pdfs=download_pdfs,
                    extract_item19=extract_item19,
                    use_cache=use_cache
                )

                all_results[state_lower] = results
                found = results.get('total_found', 0)
                total_found += found
                print(f"[{state_name.upper()}] ✅ Found {found} FDDs")

            except Exception as e:
                print(f"[{state_name.upper()}] ❌ Error: {e}")
                all_results[state_lower] = {
                    "error": str(e),
                    "source": state_lower,
                    "total_found": 0,
                    "results": []
                }

        # Deduplicate
        deduplicated = self._deduplicate(all_results)

        return {
            "source": "fdd_aggregator",
            "search_date": datetime.now().isoformat(),
            "industry": industry,
            "total_states_searched": len(states),
            "states_searched": states,
            "total_found_before_dedup": total_found,
            "total_unique": len(deduplicated),
            "by_state": all_results,
            "deduplicated": deduplicated
        }

    def _deduplicate(self, all_results: Dict[str, Dict]) -> List[Dict]:
        """
        Remove duplicate FDDs across states.

        Deduplication logic:
        - Same franchise name + year = duplicate
        - Keep version with: PDF downloaded > Item 19 extracted > larger state > alphabetically first

        Args:
            all_results: Dict of {state_name: state_results}

        Returns:
            List of unique FDD dicts with state provenance
        """
        seen = {}  # Key: (franchise_name, year) -> Value: FDD dict

        for state_name, state_data in all_results.items():
            # Skip errored sources
            if "error" in state_data:
                continue

            results = state_data.get("results", [])

            for fdd in results:
                franchise_name = fdd.get("franchise_name", "").strip().lower()
                fdd_year = fdd.get("fdd_year", 0)

                if not franchise_name:
                    continue

                key = (franchise_name, fdd_year)

                # Track which state this came from
                fdd_with_state = {**fdd, "source_state": state_name}

                # First time seeing this franchise+year
                if key not in seen:
                    seen[key] = fdd_with_state
                else:
                    # Already seen - keep better version
                    if self._is_better_version(fdd_with_state, seen[key]):
                        seen[key] = fdd_with_state

        # Convert to sorted list (by franchise name, then year descending)
        deduplicated = list(seen.values())
        deduplicated.sort(
            key=lambda x: (
                x.get("franchise_name", "").lower(),
                -x.get("fdd_year", 0)
            )
        )

        return deduplicated

    def _is_better_version(self, new: Dict, existing: Dict) -> bool:
        """
        Determine which FDD version to keep.

        Priority (in order):
        1. Has PDF downloaded (vs no PDF)
        2. Has Item 19 extracted (vs no Item 19)
        3. Larger state by market size (CA > NY > IL > MN > WI > other)
        4. Alphabetically first state name

        Args:
            new: New FDD dict
            existing: Existing FDD dict

        Returns:
            True if new version is better, False otherwise
        """
        # Priority 1: PDF downloaded
        new_has_pdf = bool(new.get("pdf_path"))
        existing_has_pdf = bool(existing.get("pdf_path"))

        if new_has_pdf and not existing_has_pdf:
            return True
        if existing_has_pdf and not new_has_pdf:
            return False

        # Priority 2: Item 19 extracted
        new_has_item19 = new.get("has_item_19", False)
        existing_has_item19 = existing.get("has_item_19", False)

        if new_has_item19 and not existing_has_item19:
            return True
        if existing_has_item19 and not new_has_item19:
            return False

        # Priority 3: State size (market share)
        state_priority = {
            'california': 1,      # 30% market
            'nasaa_fred': 2,      # 46% market (7 states)
            'minnesota': 3,       # 15% market
            'wisconsin': 4        # 11% market
        }

        new_state = new.get("source_state", "")
        existing_state = existing.get("source_state", "")

        new_priority = state_priority.get(new_state, 999)
        existing_priority = state_priority.get(existing_state, 999)

        if new_priority < existing_priority:
            return True
        if existing_priority < new_priority:
            return False

        # Priority 4: Alphabetically first
        return new_state < existing_state

    def get_coverage_stats(self) -> Dict[str, Any]:
        """
        Get coverage statistics for all FDD data_sources.

        Returns:
            Dict with state coverage info
        """
        return {
            "total_sources": len(self.scrapers),
            "sources": {
                "minnesota": {
                    "name": "Minnesota CARDS",
                    "url": "https://www.cards.commerce.state.mn.us/",
                    "states_covered": ["MN"],
                    "market_share": "~15%",
                    "estimated_brands": "2,000-3,000"
                },
                "wisconsin": {
                    "name": "Wisconsin DFI",
                    "url": "https://apps.dfi.wi.gov/apps/FranchiseSearch/",
                    "states_covered": ["WI"],
                    "market_share": "~11%",
                    "estimated_brands": "1,500-2,000"
                },
                "nasaa_fred": {
                    "name": "NASAA FRED",
                    "url": "https://www.nasaaefd.org/Franchise/Search",
                    "states_covered": ["NY", "IL", "MD", "VA", "WA", "ND", "RI"],
                    "market_share": "~46%",
                    "estimated_brands": "3,000-4,000"
                },
                "california": {
                    "name": "California DocQNet",
                    "url": "https://docqnet.dfpi.ca.gov/search/",
                    "states_covered": ["CA"],
                    "market_share": "~30%",
                    "estimated_brands": "4,000-5,000"
                }
            },
            "total_states": 10,
            "total_market_share": "90%+",
            "estimated_total_brands": "15,000-20,000",
            "estimated_total_documents": "30,000-40,000"
        }


if __name__ == "__main__":
    # Example usage
    agg = FDDAggregator()

    # Search all sources
    print("\n" + "="*70)
    print("Example: Search all FDD sources for 'car wash'")
    print("="*70)

    results = agg.search_all(
        industry="car wash",
        max_results_per_source=5,
        download_pdfs=False,
        use_cache=True
    )

    print(f"\nRESULTS SUMMARY:")
    print(f"- Total found (before dedup): {results['total_found_before_dedup']}")
    print(f"- Unique FDDs: {results['total_unique']}")
    print(f"- States searched: {results['total_states_searched']}")

    print(f"\nBY STATE:")
    for state, data in results['by_state'].items():
        if 'error' in data:
            print(f"  {state}: ERROR - {data['error']}")
        else:
            print(f"  {state}: {data['total_found']} found")

    print(f"\nDEDUPLICATED RESULTS:")
    for fdd in results['deduplicated'][:5]:  # Show first 5
        print(f"  - {fdd['franchise_name']} ({fdd.get('fdd_year', 'N/A')}) from {fdd['source_state']}")

    # Coverage stats
    print("\n" + "="*70)
    print("COVERAGE STATISTICS")
    print("="*70)
    stats = agg.get_coverage_stats()
    print(f"Total sources: {stats['total_sources']}")
    print(f"Total states: {stats['total_states']}")
    print(f"Market coverage: {stats['total_market_share']}")
    print(f"Estimated brands: {stats['estimated_total_brands']}")
