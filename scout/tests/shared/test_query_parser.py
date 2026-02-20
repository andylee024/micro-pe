"""Tests for query parser"""

import pytest
from scout.shared.query_parser import parse_query


class TestQueryParser:
    """Test cases for query parsing"""

    def test_standard_in_pattern(self):
        """Test standard 'industry in location' pattern"""
        industry, location = parse_query("HVAC in Los Angeles")
        assert industry == "HVAC"
        assert location == "Los Angeles"

    def test_with_businesses_keyword(self):
        """Test query with 'businesses' keyword"""
        industry, location = parse_query("HVAC businesses in Los Angeles")
        assert industry == "HVAC"
        assert location == "Los Angeles"

    def test_near_keyword(self):
        """Test 'near' keyword instead of 'in'"""
        industry, location = parse_query("car wash near San Diego")
        assert industry == "car wash"
        assert location == "San Diego"

    def test_multi_word_industry(self):
        """Test multi-word industry names"""
        industry, location = parse_query("auto repair shops in Houston")
        assert industry == "auto repair"
        assert location == "Houston"

    def test_multi_word_location(self):
        """Test multi-word location names"""
        industry, location = parse_query("HVAC in New York City")
        assert industry == "HVAC"
        assert location == "New York City"

    def test_location_with_state(self):
        """Test location with state name"""
        industry, location = parse_query("laundromats in Phoenix, Arizona")
        assert industry == "laundromats"
        assert location == "Phoenix, Arizona"

    def test_location_with_state_abbr(self):
        """Test location with state abbreviation"""
        industry, location = parse_query("car wash in Houston, TX")
        assert industry == "car wash"
        assert location == "Houston, TX"

    def test_simple_format_with_state(self):
        """Test simple 'industry location' format with state"""
        industry, location = parse_query("HVAC Los Angeles CA")
        assert industry == "HVAC"
        assert "Los Angeles" in location or location == "Los Angeles CA"

    def test_simple_format_city_state(self):
        """Test simple format with city and state"""
        industry, location = parse_query("laundromat San Diego California")
        assert industry == "laundromat"
        assert "San Diego" in location

    def test_companies_keyword(self):
        """Test with 'companies' keyword"""
        industry, location = parse_query("HVAC companies in Dallas")
        assert industry == "HVAC"
        assert location == "Dallas"

    def test_services_keyword(self):
        """Test with 'services' keyword"""
        industry, location = parse_query("plumbing services in Seattle")
        assert industry == "plumbing"
        assert location == "Seattle"

    def test_case_insensitive(self):
        """Test that parsing is case-insensitive for keywords"""
        industry, location = parse_query("hvac IN los angeles")
        assert industry == "hvac"
        assert location == "los angeles"

    def test_extra_whitespace(self):
        """Test query with extra whitespace"""
        industry, location = parse_query("  HVAC   in   Los Angeles  ")
        assert industry == "HVAC"
        assert location == "Los Angeles"

    def test_empty_query_raises_error(self):
        """Test that empty query raises ValueError"""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            parse_query("")

    def test_whitespace_only_query_raises_error(self):
        """Test that whitespace-only query raises ValueError"""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            parse_query("   ")

    def test_missing_location_raises_error(self):
        """Test that query without location raises ValueError"""
        with pytest.raises(ValueError, match="Could not parse query"):
            parse_query("HVAC")

    def test_missing_industry_raises_error(self):
        """Test that query without industry raises ValueError"""
        with pytest.raises(ValueError, match="Could not parse query"):
            parse_query("near Chicago")

    def test_with_shop_keyword(self):
        """Test with 'shop' keyword"""
        industry, location = parse_query("auto repair shop in Miami")
        assert industry == "auto repair"
        assert location == "Miami"

    def test_major_city_detection(self):
        """Test detection of major cities"""
        industry, location = parse_query("pizza San Francisco")
        assert industry == "pizza"
        assert location == "San Francisco"

    def test_stores_keyword(self):
        """Test with 'stores' keyword"""
        industry, location = parse_query("convenience stores in Atlanta")
        assert industry == "convenience"
        assert location == "Atlanta"


class TestLocationDetection:
    """Test cases specifically for location detection logic"""

    def test_state_in_location(self):
        """Test that state names are recognized"""
        industry, location = parse_query("HVAC Phoenix Arizona")
        assert industry == "HVAC"
        assert "Arizona" in location or "Phoenix" in location

    def test_state_abbr_in_location(self):
        """Test that state abbreviations are recognized"""
        industry, location = parse_query("pizza Chicago IL")
        assert industry == "pizza"
        assert "Chicago" in location or "IL" in location

    def test_new_prefix_states(self):
        """Test states with 'New' prefix"""
        industry, location = parse_query("bakery in New Jersey")
        assert industry == "bakery"
        assert location == "New Jersey"

    def test_compound_state_names(self):
        """Test compound state names"""
        industry, location = parse_query("cafe in North Carolina")
        assert industry == "cafe"
        assert location == "North Carolina"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
