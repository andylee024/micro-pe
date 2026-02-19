"""Parse natural language queries into industry and location"""

import re
from typing import Tuple


def parse_query(query: str) -> Tuple[str, str]:
    """
    Parse natural language query into (industry, location).

    Handles various patterns:
    - "HVAC businesses in Los Angeles" → ("HVAC", "Los Angeles")
    - "car wash in San Diego" → ("car wash", "San Diego")
    - "HVAC near Los Angeles" → ("HVAC", "Los Angeles")
    - "Los Angeles HVAC" → ("HVAC", "Los Angeles")
    - "HVAC Los Angeles" → ("HVAC", "Los Angeles")

    Args:
        query: Natural language query string

    Returns:
        Tuple of (industry, location)

    Raises:
        ValueError: If query cannot be parsed or missing required components
    """
    query = query.strip()

    if not query:
        raise ValueError("Query cannot be empty")

    # Pattern 1: "X in Y" or "X near Y"
    pattern1 = r'^(.+?)\s+(?:in|near)\s+(.+?)$'
    match = re.match(pattern1, query, re.IGNORECASE)
    if match:
        industry = match.group(1).strip()
        location = match.group(2).strip()
        # Clean up industry (remove "businesses", "companies", etc.)
        industry = _clean_industry(industry)
        # Validate industry is not empty after cleaning
        if not industry or len(industry.strip()) == 0:
            raise ValueError(
                f"Could not parse query: '{query}'. "
                "Industry is missing or invalid."
            )
        return (industry, location)

    # Pattern 2: "Y X" - location comes first (less common)
    # Try to detect if first word(s) is a known location pattern
    # This is harder to detect reliably, so we'll be conservative

    # Pattern 3: "X Y" - split on last few words that might be location
    # Try to find common location indicators
    words = query.split()
    if len(words) >= 2:
        # Try splitting at different points, starting from the end
        # This prioritizes longer locations over longer industries
        for split_idx in range(1, len(words)):
            potential_industry = ' '.join(words[:split_idx])
            potential_location = ' '.join(words[split_idx:])

            # Check if potential_location looks like a location
            if _looks_like_location(potential_location):
                industry = _clean_industry(potential_industry)
                # Only return if we have a valid industry (not empty and not just a preposition)
                if industry and not _is_invalid_industry(industry):
                    return (industry, potential_location)

    # If no clear pattern, raise error
    raise ValueError(
        f"Could not parse query: '{query}'. "
        "Expected format: 'industry in location' (e.g., 'HVAC in Los Angeles')"
    )


def _is_invalid_industry(industry: str) -> bool:
    """Check if industry is invalid (just prepositions/keywords)"""
    invalid_words = ['in', 'near', 'at', 'on', 'by', 'the', 'a', 'an']
    return industry.lower().strip() in invalid_words


def _clean_industry(industry: str) -> str:
    """Remove common filler words from industry"""
    # Remove "businesses", "companies", "services", etc.
    filler_words = [
        'businesses', 'business', 'companies', 'company',
        'services', 'service', 'shops', 'shop', 'stores', 'store'
    ]

    words = industry.split()
    cleaned_words = [w for w in words if w.lower() not in filler_words]

    if not cleaned_words:
        # If we removed everything, return original
        return industry

    return ' '.join(cleaned_words)


def _looks_like_location(text: str) -> bool:
    """Check if text looks like a location"""
    # Simple heuristic: check for common location patterns
    text_lower = text.lower()

    # Contains state abbreviations or full state names
    us_states = [
        'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado',
        'connecticut', 'delaware', 'florida', 'georgia', 'hawaii', 'idaho',
        'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana',
        'maine', 'maryland', 'massachusetts', 'michigan', 'minnesota',
        'mississippi', 'missouri', 'montana', 'nebraska', 'nevada',
        'new hampshire', 'new jersey', 'new mexico', 'new york',
        'north carolina', 'north dakota', 'ohio', 'oklahoma', 'oregon',
        'pennsylvania', 'rhode island', 'south carolina', 'south dakota',
        'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington',
        'west virginia', 'wisconsin', 'wyoming'
    ]

    us_state_abbr = [
        'al', 'ak', 'az', 'ar', 'ca', 'co', 'ct', 'de', 'fl', 'ga', 'hi', 'id',
        'il', 'in', 'ia', 'ks', 'ky', 'la', 'me', 'md', 'ma', 'mi', 'mn', 'ms',
        'mo', 'mt', 'ne', 'nv', 'nh', 'nj', 'nm', 'ny', 'nc', 'nd', 'oh', 'ok',
        'or', 'pa', 'ri', 'sc', 'sd', 'tn', 'tx', 'ut', 'vt', 'va', 'wa', 'wv',
        'wi', 'wy'
    ]

    # Check if contains state name or abbreviation
    for state in us_states:
        if state in text_lower:
            return True

    # Check for state abbreviations as separate words or at end
    words = text_lower.split()

    # Check last word for state abbreviation (common pattern: "Los Angeles CA")
    if words and words[-1] in us_state_abbr:
        return True

    # Check any word for state abbreviation
    for abbr in us_state_abbr:
        if abbr in words:
            return True

    # Check for common city names (major cities)
    major_cities = [
        'new york', 'los angeles', 'chicago', 'houston', 'phoenix', 'philadelphia',
        'san antonio', 'san diego', 'dallas', 'san jose', 'austin', 'jacksonville',
        'san francisco', 'columbus', 'fort worth', 'indianapolis', 'charlotte',
        'seattle', 'denver', 'washington', 'boston', 'detroit', 'nashville',
        'memphis', 'portland', 'oklahoma city', 'las vegas', 'baltimore', 'milwaukee',
        'albuquerque', 'tucson', 'fresno', 'sacramento', 'kansas city', 'atlanta',
        'miami', 'orlando', 'tampa', 'pittsburgh', 'cleveland', 'cincinnati',
        'minneapolis', 'new orleans'
    ]

    for city in major_cities:
        if city in text_lower:
            return True

    # Check for "city" or "county" in the text
    if 'city' in text_lower or 'county' in text_lower:
        return True

    # If text is short (1-2 words) and contains title case, might be a city
    if len(words) <= 3 and any(w[0].isupper() for w in text.split() if w):
        return True

    return False
