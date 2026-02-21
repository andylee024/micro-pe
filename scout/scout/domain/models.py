"""Core domain models for Scout."""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Business:
    name: str
    address: str = ""
    phone: str = ""
    website: str = ""
    category: str = ""
    rating: Optional[float] = None
    reviews: Optional[int] = None
    place_id: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    estimated_revenue: Optional[float] = None
    estimated_cash_flow: Optional[float] = None
    estimated_value: Optional[float] = None
    confidence: Optional[str] = None


@dataclass
class Benchmark:
    industry: str
    median_revenue: Optional[float] = None
    median_cash_flow: Optional[float] = None
    median_multiple: Optional[float] = None
    margin_pct: Optional[float] = None
    sample_size: int = 0
    source: str = ""


@dataclass
class MarketSummary:
    industry: str
    location: str
    total_businesses: int
    query: str = ""
    benchmarks: List[Benchmark] = field(default_factory=list)


@dataclass
class ResearchResult:
    summary: MarketSummary
    businesses: List[Business]
    pulse: dict = field(default_factory=dict)
    market_overview: dict = field(default_factory=dict)
