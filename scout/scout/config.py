"""Configuration management for Scout"""

from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Keys
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY') or os.getenv('GOOGLE_PLACES_API_KEY')

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
CACHE_DIR = OUTPUT_DIR / "cache"

# Constants
CACHE_TTL_DAYS = 90  # Cache for 90 days
MAX_RESULTS_DEFAULT = 500

# Validation
if not GOOGLE_MAPS_API_KEY:
    raise ValueError(
        "GOOGLE_MAPS_API_KEY not found in .env file. "
        "Please add it to your .env file or set GOOGLE_PLACES_API_KEY environment variable."
    )

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
