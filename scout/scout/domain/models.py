"""Core domain models for Scout."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


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
class MarketFinancials:
    fdd_count: int = 0
    confidence: str = "—"
    median_revenue: str = "—"
    revenue_range: str = ""
    ebitda_margin: str = "—"
    margin_range: str = ""
    typical_acquisition: str = "—"

    @classmethod
    def from_dict(cls, data: Dict[str, Any] | None) -> "MarketFinancials":
        data = data or {}
        return cls(
            fdd_count=_safe_int(data.get("fdd_count", 0), 0),
            confidence=data.get("confidence", "—"),
            median_revenue=data.get("median_revenue", "—"),
            revenue_range=data.get("revenue_range", ""),
            ebitda_margin=data.get("ebitda_margin", "—"),
            margin_range=data.get("margin_range", ""),
            typical_acquisition=data.get("typical_acquisition", "—"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fdd_count": self.fdd_count,
            "confidence": self.confidence,
            "median_revenue": self.median_revenue,
            "revenue_range": self.revenue_range,
            "ebitda_margin": self.ebitda_margin,
            "margin_range": self.margin_range,
            "typical_acquisition": self.typical_acquisition,
        }


@dataclass
class MarketQuality:
    avg_rating: float = 0.0
    sentiment_positive: int = 0
    review_volume: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any] | None) -> "MarketQuality":
        data = data or {}
        return cls(
            avg_rating=_safe_float(data.get("avg_rating", 0.0), 0.0),
            sentiment_positive=_safe_int(data.get("sentiment_positive", 0), 0),
            review_volume=_safe_int(data.get("review_volume", 0), 0),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "avg_rating": self.avg_rating,
            "sentiment_positive": self.sentiment_positive,
            "review_volume": self.review_volume,
        }


@dataclass
class MarketTrends:
    job_postings: str = "—"
    new_entrants: str = "—"
    search_volume: str = "—"

    @classmethod
    def from_dict(cls, data: Dict[str, Any] | None) -> "MarketTrends":
        data = data or {}
        return cls(
            job_postings=str(data.get("job_postings", "—")),
            new_entrants=str(data.get("new_entrants", "—")),
            search_volume=str(data.get("search_volume", "—")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_postings": self.job_postings,
            "new_entrants": self.new_entrants,
            "search_volume": self.search_volume,
        }


@dataclass
class MarketOutlook:
    grade: str = "—"
    note: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any] | None) -> "MarketOutlook":
        data = data or {}
        return cls(
            grade=data.get("grade", "—"),
            note=data.get("note", ""),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"grade": self.grade, "note": self.note}


@dataclass
class MarketOverviewSources:
    fdd_filings: List[Dict[str, Any]] = field(default_factory=list)
    bizbuysell: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any] | None) -> "MarketOverviewSources":
        data = data or {}
        return cls(
            fdd_filings=list(data.get("fdd_filings", []) or []),
            bizbuysell=dict(data.get("bizbuysell", {}) or {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"fdd_filings": self.fdd_filings, "bizbuysell": self.bizbuysell}


@dataclass
class MarketOverview:
    total_businesses: int = 0
    market_density: str = "—"
    est_market_value: str = ""
    financial: MarketFinancials = field(default_factory=MarketFinancials)
    quality: MarketQuality = field(default_factory=MarketQuality)
    trends: MarketTrends = field(default_factory=MarketTrends)
    outlook: MarketOutlook = field(default_factory=MarketOutlook)
    sources: MarketOverviewSources = field(default_factory=MarketOverviewSources)

    @classmethod
    def from_dict(cls, data: Dict[str, Any] | None) -> "MarketOverview":
        if isinstance(data, MarketOverview):
            return data
        data = data or {}
        return cls(
            total_businesses=_safe_int(data.get("total_businesses", 0), 0),
            market_density=data.get("market_density", "—"),
            est_market_value=data.get("est_market_value", ""),
            financial=MarketFinancials.from_dict(data.get("financial")),
            quality=MarketQuality.from_dict(data.get("quality")),
            trends=MarketTrends.from_dict(data.get("trends")),
            outlook=MarketOutlook.from_dict(data.get("outlook")),
            sources=MarketOverviewSources.from_dict(data.get("sources")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_businesses": self.total_businesses,
            "market_density": self.market_density,
            "est_market_value": self.est_market_value,
            "financial": self.financial.to_dict(),
            "quality": self.quality.to_dict(),
            "trends": self.trends.to_dict(),
            "outlook": self.outlook.to_dict(),
            "sources": self.sources.to_dict(),
        }


@dataclass
class PulseBusinessModel:
    customers: str = "—"
    revenue: str = "—"

    @classmethod
    def from_dict(cls, data: Dict[str, Any] | None) -> "PulseBusinessModel":
        data = data or {}
        return cls(
            customers=data.get("customers", "—"),
            revenue=data.get("revenue", "—"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"customers": self.customers, "revenue": self.revenue}


@dataclass
class PulseSources:
    reddit: int = 0
    reddit_threads: List[Dict[str, Any]] = field(default_factory=list)
    report_list: List[str] = field(default_factory=list)
    reviews: int = 0
    reports: int = 0
    listings: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any] | None) -> "PulseSources":
        data = data or {}
        return cls(
            reddit=_safe_int(data.get("reddit", 0), 0),
            reddit_threads=list(data.get("reddit_threads", []) or []),
            report_list=list(data.get("report_list", []) or []),
            reviews=_safe_int(data.get("reviews", 0), 0),
            reports=_safe_int(data.get("reports", 0), 0),
            listings=_safe_int(data.get("listings", 0), 0),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reddit": self.reddit,
            "reddit_threads": self.reddit_threads,
            "report_list": self.report_list,
            "reviews": self.reviews,
            "reports": self.reports,
            "listings": self.listings,
        }


@dataclass
class MarketPulse:
    business_model: PulseBusinessModel = field(default_factory=PulseBusinessModel)
    operating_models: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    sources: PulseSources = field(default_factory=PulseSources)

    @classmethod
    def from_dict(cls, data: Dict[str, Any] | None) -> "MarketPulse":
        if isinstance(data, MarketPulse):
            return data
        data = data or {}
        return cls(
            business_model=PulseBusinessModel.from_dict(data.get("business_model")),
            operating_models=list(data.get("operating_models", []) or []),
            opportunities=list(data.get("opportunities", []) or []),
            risks=list(data.get("risks", []) or []),
            sources=PulseSources.from_dict(data.get("sources")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "business_model": self.business_model.to_dict(),
            "operating_models": self.operating_models,
            "opportunities": self.opportunities,
            "risks": self.risks,
            "sources": self.sources.to_dict(),
        }

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
    pulse: MarketPulse = field(default_factory=MarketPulse)
    market_overview: MarketOverview = field(default_factory=MarketOverview)
