"""Unified settings for Scout (non-throwing, environment-driven)."""

from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Central settings used by CLI and UI."""

    # API keys
    google_maps_api_key: str | None = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("GOOGLE_PLACES_API_KEY")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY") or ""

    # Paths
    project_root: Path = Path(__file__).resolve().parents[2]
    output_dir: Path = project_root / "outputs"
    cache_dir: Path = output_dir / "cache"

    # Defaults
    cache_ttl_days: int = 90
    max_results_default: int = 500


settings = Settings()
