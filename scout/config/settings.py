"""
Configuration management
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""

    # API Keys
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

    # Output directory
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'outputs')

    # Scraper settings
    MAX_GOOGLE_MAPS_RESULTS = 60
    MAX_BIZBUYSELL_LISTINGS = 20

    # Rate limiting
    BIZBUYSELL_DELAY_SECONDS = 2

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []

        if not cls.GOOGLE_MAPS_API_KEY or cls.GOOGLE_MAPS_API_KEY == 'your_api_key_here':
            errors.append("GOOGLE_MAPS_API_KEY not set in .env file")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

        return True
