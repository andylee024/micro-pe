"""Configuration management for Scout (compatibility wrapper)."""

from scout.shared.settings import settings

# API Keys
GOOGLE_MAPS_API_KEY = settings.google_maps_api_key
ANTHROPIC_API_KEY: str = settings.anthropic_api_key

# Paths
PROJECT_ROOT = settings.project_root
OUTPUT_DIR = settings.output_dir
CACHE_DIR = settings.cache_dir

# Constants
CACHE_TTL_DAYS = settings.cache_ttl_days
MAX_RESULTS_DEFAULT = settings.max_results_default

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
