"""Integration tests for Scout V0 end-to-end functionality"""

import pytest
import csv
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def mock_google_maps_response():
    """Mock Google Maps API response"""
    return [
        {
            'name': 'Cool Air HVAC',
            'address': '1234 Wilshire Blvd, Los Angeles, CA 90010',
            'phone': '(310) 555-0100',
            'website': 'coolair.com',
            'category': 'HVAC'
        },
        {
            'name': 'Premier Climate',
            'address': '456 Main St, Santa Monica, CA 90401',
            'phone': '(310) 555-0200',
            'website': 'premierclimate.com',
            'category': 'HVAC'
        },
        {
            'name': 'SoCal Heating & Air',
            'address': '789 Oak Ave, Pasadena, CA 91101',
            'phone': '(626) 555-0300',
            'website': 'socalheating.com',
            'category': 'HVAC'
        }
    ]


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory"""
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    return output_dir


def test_full_export_pipeline(mock_google_maps_response, temp_output_dir):
    """Test complete pipeline: fetch data -> export to CSV"""
    from scout.shared.export import export_to_csv

    # Simulate the full pipeline
    businesses = mock_google_maps_response
    industry = "HVAC"
    location = "Los Angeles, CA"

    # Export to CSV
    csv_path = export_to_csv(
        businesses,
        industry,
        location,
        output_dir=temp_output_dir
    )

    # Verify file exists
    assert csv_path.exists()

    # Verify CSV content
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        assert len(rows) == len(businesses)
        assert rows[0]['name'] == 'Cool Air HVAC'
        assert rows[1]['name'] == 'Premier Climate'
        assert rows[2]['name'] == 'SoCal Heating & Air'


def test_error_handling_empty_results(temp_output_dir):
    """Test that empty results are handled gracefully"""
    from scout.shared.export import export_to_csv

    businesses = []

    with pytest.raises(ValueError, match="Cannot export empty business list"):
        export_to_csv(businesses, "HVAC", "Los Angeles, CA", output_dir=temp_output_dir)


def test_error_handling_missing_api_key():
    """Test that missing API key raises appropriate error"""
    from scout.shared.errors import validate_api_key, ConfigurationError

    with pytest.raises(ConfigurationError, match="API key is missing"):
        validate_api_key(None, "Google Maps")

    with pytest.raises(ConfigurationError, match="API key is missing"):
        validate_api_key("", "Google Maps")

    with pytest.raises(ConfigurationError, match="API key is missing"):
        validate_api_key("   ", "Google Maps")


def test_error_handling_invalid_query():
    """Test that invalid queries are handled gracefully"""
    from scout.shared.errors import validate_industry, validate_location, ValidationError

    # Test empty industry
    with pytest.raises(ValidationError, match="Industry cannot be empty"):
        validate_industry("")

    with pytest.raises(ValidationError, match="Industry must be at least 2 characters"):
        validate_industry("H")

    # Test empty location
    with pytest.raises(ValidationError, match="Location cannot be empty"):
        validate_location("")

    with pytest.raises(ValidationError, match="Location must be at least 2 characters"):
        validate_location("L")


def test_error_message_formatting():
    """Test that error messages are user-friendly"""
    from scout.shared.errors import (
        APIError, NetworkError, FileIOError,
        format_error_message
    )

    # Test API error
    api_error = APIError("Connection failed", api_name="Google Maps")
    message = format_error_message(api_error)
    assert "❌ Error:" in message
    assert "GOOGLE_MAPS_API_KEY" in message

    # Test network error
    network_error = NetworkError("No internet connection")
    message = format_error_message(network_error)
    assert "❌ Error:" in message
    assert "internet connection" in message

    # Test file IO error
    file_error = FileIOError("Permission denied")
    message = format_error_message(file_error)
    assert "❌ Error:" in message
    assert "file permissions" in message.lower()


def test_api_error_handling():
    """Test API error handling and conversion"""
    from scout.shared.errors import handle_api_error, APIError

    # Test timeout error
    timeout_error = Exception("Request timeout after 30 seconds")
    api_error = handle_api_error(timeout_error, "Google Maps")
    assert isinstance(api_error, APIError)
    assert "timed out" in str(api_error).lower() or "timeout" in str(api_error).lower()

    # Test connection error
    connection_error = Exception("Connection refused")
    api_error = handle_api_error(connection_error, "Google Maps")
    assert "connect" in str(api_error).lower()

    # Test authentication error
    auth_error = Exception("Unauthorized - invalid API key")
    api_error = handle_api_error(auth_error, "Google Maps")
    assert "authentication" in str(api_error).lower()


def test_file_error_handling():
    """Test file error handling and conversion"""
    from scout.shared.errors import handle_file_error, FileIOError

    # Test permission error
    perm_error = Exception("Permission denied")
    file_error = handle_file_error(perm_error, "/path/to/file.csv", "write")
    assert isinstance(file_error, FileIOError)
    assert "permission" in str(file_error).lower()

    # Test file not found error
    not_found_error = Exception("No such file or directory")
    file_error = handle_file_error(not_found_error, "/path/to/file.csv", "read")
    assert "not found" in str(file_error).lower()


def test_safe_execute_success():
    """Test safe_execute with successful function"""
    from scout.shared.errors import safe_execute

    def successful_function(x, y):
        return x + y

    success, result = safe_execute(successful_function, 5, 10)

    assert success is True
    assert result == 15


def test_safe_execute_failure():
    """Test safe_execute with failing function"""
    from scout.shared.errors import safe_execute

    def failing_function():
        raise ValueError("Something went wrong")

    success, result = safe_execute(failing_function, error_message="Operation failed")

    assert success is False
    assert "Operation failed" in result
    assert "❌" in result


def test_handle_errors_decorator_success():
    """Test handle_errors decorator with successful function"""
    from scout.shared.errors import handle_errors

    @handle_errors(default_return=None)
    def successful_function():
        return "success"

    result = successful_function()
    assert result == "success"


def test_handle_errors_decorator_failure():
    """Test handle_errors decorator with failing function"""
    from scout.shared.errors import handle_errors

    @handle_errors(default_return=[])
    def failing_function():
        raise ValueError("Test error")

    result = failing_function()
    assert result == []


def test_export_with_partial_data(temp_output_dir):
    """Test that export handles businesses with missing fields"""
    from scout.shared.export import export_to_csv

    businesses = [
        {'name': 'Complete Business', 'address': '123 Main St', 'phone': '555-0100', 'website': 'test.com'},
        {'name': 'Partial Business', 'phone': '555-0200'},  # Missing address and website
        {'name': 'Another Partial'},  # Only has name
    ]

    csv_path = export_to_csv(
        businesses,
        "HVAC",
        "Los Angeles, CA",
        output_dir=temp_output_dir
    )

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        assert len(rows) == 3

        # First business should have all fields
        assert rows[0]['name'] == 'Complete Business'
        assert rows[0]['address'] == '123 Main St'

        # Second business should have N/A for missing fields
        assert rows[1]['name'] == 'Partial Business'
        assert rows[1]['address'] == 'N/A'
        assert rows[1]['website'] == 'N/A'

        # Third business should have N/A for most fields
        assert rows[2]['name'] == 'Another Partial'
        assert rows[2]['address'] == 'N/A'
        assert rows[2]['phone'] == 'N/A'


def test_concurrent_exports(mock_google_maps_response, temp_output_dir):
    """Test that multiple exports can happen without conflicts"""
    from scout.shared.export import export_to_csv

    # Export same industry, different locations
    path1 = export_to_csv(
        mock_google_maps_response,
        "HVAC",
        "Los Angeles, CA",
        output_dir=temp_output_dir
    )

    path2 = export_to_csv(
        mock_google_maps_response,
        "HVAC",
        "San Diego, CA",
        output_dir=temp_output_dir
    )

    # Should create different files
    assert path1 != path2
    assert path1.exists()
    assert path2.exists()


def test_large_dataset_export(temp_output_dir):
    """Test export performance with large dataset"""
    from scout.shared.export import export_to_csv

    # Create 1000 businesses
    businesses = [
        {
            'name': f'Business {i}',
            'address': f'{i} Main St, Los Angeles, CA',
            'phone': f'(555) {i:04d}',
            'website': f'business{i}.com',
            'category': 'HVAC'
        }
        for i in range(1000)
    ]

    csv_path = export_to_csv(
        businesses,
        "HVAC",
        "Los Angeles, CA",
        output_dir=temp_output_dir
    )

    # Verify all rows exported
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        assert len(rows) == 1000
        assert rows[0]['name'] == 'Business 0'
        assert rows[999]['name'] == 'Business 999'


def test_export_message_formatting():
    """Test export success message formatting"""
    from scout.shared.export import format_export_message

    path = Path("outputs/hvac_los_angeles_2026-02-19.csv")
    message = format_export_message(path, 487)

    # Verify message components
    assert "✅" in message
    assert "Exported to:" in message
    assert "hvac_los_angeles" in message
    assert "Columns:" in message
    assert "name, address, phone, website, category" in message
    assert "Rows: 487 businesses" in message


def test_validation_pipeline():
    """Test full validation pipeline"""
    from scout.shared.errors import (
        validate_api_key, validate_industry, validate_location,
        ConfigurationError, ValidationError
    )

    # Valid inputs should pass
    validate_api_key("test_key_12345", "Google Maps")
    validate_industry("HVAC")
    validate_location("Los Angeles, CA")

    # Invalid inputs should raise errors
    with pytest.raises(ConfigurationError):
        validate_api_key("", "Google Maps")

    with pytest.raises(ValidationError):
        validate_industry("")

    with pytest.raises(ValidationError):
        validate_location("")
