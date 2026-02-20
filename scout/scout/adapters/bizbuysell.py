"""BizBuySell adapter (best-effort) returning benchmark inputs."""

from typing import List, Dict
from data_sources.marketplaces.bizbuysell import BizBuySellTool


class BizBuySellAdapter:
    def __init__(self):
        self.tool = BizBuySellTool()

    def search(self, industry: str, max_results: int = 20, use_cache: bool = True) -> List[Dict]:
        try:
            result = self.tool.search(
                industry=industry,
                max_results=max_results,
                use_cache=use_cache,
            )
            return result.get("results", [])
        except Exception:
            return []
