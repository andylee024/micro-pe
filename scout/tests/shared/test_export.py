"""Tests for CSV export functionality"""

import pytest
import csv
from pathlib import Path
from datetime import datetime
from scout.shared.export import export_to_csv, format_export_message


@pytest.fixture
def sample_businesses():
    """Sample business data for testing"""
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


def test_export_creates_file(sample_businesses, temp_output_dir):
    """Test that export creates a CSV file"""
    path = export_to_csv(
        sample_businesses,
        "HVAC",
        "Los Angeles, CA",
        output_dir=temp_output_dir
    )

    assert path.exists()
    assert path.suffix == '.csv'


def test_export_filename_format(sample_businesses, temp_output_dir):
    """Test that filename follows correct format"""
    path = export_to_csv(
        sample_businesses,
        "HVAC",
        "Los Angeles, CA",
        output_dir=temp_output_dir
    )

    # Should be: hvac_los_angeles_ca_2026-02-19.csv
    assert 'hvac' in path.name.lower()
    assert 'los_angeles' in path.name.lower()
    assert datetime.now().strftime('%Y-%m-%d') in path.name


def test_export_filename_sanitization(sample_businesses, temp_output_dir):
    """Test that filename handles special characters"""
    path = export_to_csv(
        sample_businesses,
        "HVAC-Repair Services",
        "Los Angeles, CA",
        output_dir=temp_output_dir
    )

    # Should replace spaces with underscores and remove commas
    assert ' ' not in path.name
    assert ',' not in path.name
    assert 'hvac_repair_services' in path.name.lower()


def test_export_csv_format(sample_businesses, temp_output_dir):
    """Test that CSV has correct format with headers"""
    path = export_to_csv(
        sample_businesses,
        "HVAC",
        "Los Angeles, CA",
        output_dir=temp_output_dir
    )

    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        # Check headers
        assert reader.fieldnames == ['name', 'address', 'phone', 'website', 'category']

        # Check number of rows
        assert len(rows) == 3

        # Check first row data
        assert rows[0]['name'] == 'Cool Air HVAC'
        assert rows[0]['phone'] == '(310) 555-0100'
        assert rows[0]['website'] == 'coolair.com'


def test_export_all_businesses(sample_businesses, temp_output_dir):
    """Test that all businesses are exported"""
    path = export_to_csv(
        sample_businesses,
        "HVAC",
        "Los Angeles, CA",
        output_dir=temp_output_dir
    )

    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        assert len(rows) == len(sample_businesses)

        # Verify each business is present
        exported_names = [row['name'] for row in rows]
        for business in sample_businesses:
            assert business['name'] in exported_names


def test_export_empty_list_raises_error(temp_output_dir):
    """Test that exporting empty list raises ValueError"""
    with pytest.raises(ValueError, match="Cannot export empty business list"):
        export_to_csv([], "HVAC", "Los Angeles, CA", output_dir=temp_output_dir)


def test_export_missing_fields(temp_output_dir):
    """Test that businesses with missing fields get N/A"""
    businesses = [
        {'name': 'Test Business'},  # Missing most fields
        {'name': 'Another Business', 'phone': '123-456-7890'}  # Missing some fields
    ]

    path = export_to_csv(
        businesses,
        "HVAC",
        "Los Angeles, CA",
        output_dir=temp_output_dir
    )

    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        # First business should have N/A for missing fields
        assert rows[0]['name'] == 'Test Business'
        assert rows[0]['address'] == 'N/A'
        assert rows[0]['phone'] == 'N/A'
        assert rows[0]['website'] == 'N/A'

        # Second business should have phone but N/A for others
        assert rows[1]['phone'] == '123-456-7890'
        assert rows[1]['address'] == 'N/A'


def test_export_creates_directory(sample_businesses, tmp_path):
    """Test that export creates output directory if it doesn't exist"""
    output_dir = tmp_path / "nonexistent" / "outputs"

    path = export_to_csv(
        sample_businesses,
        "HVAC",
        "Los Angeles, CA",
        output_dir=output_dir
    )

    assert output_dir.exists()
    assert path.exists()


def test_export_overwrites_existing_file(sample_businesses, temp_output_dir):
    """Test that export overwrites file with same name"""
    # Export once
    path1 = export_to_csv(
        sample_businesses,
        "HVAC",
        "Los Angeles, CA",
        output_dir=temp_output_dir
    )

    # Export again with different data
    modified_businesses = [sample_businesses[0]]  # Only one business
    path2 = export_to_csv(
        modified_businesses,
        "HVAC",
        "Los Angeles, CA",
        output_dir=temp_output_dir
    )

    # Paths should be the same (same day)
    assert path1 == path2

    # File should have only 1 business now
    with open(path2, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1


def test_format_export_message_default():
    """Test format_export_message with default parameters"""
    path = Path("outputs/hvac_los_angeles_2026-02-19.csv")
    message = format_export_message(path, 487)

    assert "✅ Exported to:" in message
    assert "outputs/hvac_los_angeles_2026-02-19.csv" in message
    assert "Columns: name, address, phone, website, category" in message
    assert "Rows: 487 businesses" in message


def test_format_export_message_custom_columns():
    """Test format_export_message with custom column names"""
    path = Path("outputs/test.csv")
    message = format_export_message(path, 100, fieldnames=['name', 'phone'])

    assert "Columns: name, phone" in message
    assert "Rows: 100 businesses" in message


def test_export_handles_unicode(temp_output_dir):
    """Test that export handles Unicode characters correctly"""
    businesses = [
        {
            'name': 'Café HVAC',
            'address': '123 Rue de la Paix, Paris',
            'phone': '+33 1 23 45 67 89',
            'website': 'café-hvac.com',
            'category': 'HVAC'
        }
    ]

    path = export_to_csv(
        businesses,
        "HVAC",
        "Paris, France",
        output_dir=temp_output_dir
    )

    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        assert rows[0]['name'] == 'Café HVAC'
        assert 'Rue de la Paix' in rows[0]['address']


def test_export_large_dataset(temp_output_dir):
    """Test export with large number of businesses"""
    # Create 500 businesses
    businesses = [
        {
            'name': f'Business {i}',
            'address': f'{i} Main St',
            'phone': f'(555) {i:03d}-0000',
            'website': f'business{i}.com',
            'category': 'HVAC'
        }
        for i in range(500)
    ]

    path = export_to_csv(
        businesses,
        "HVAC",
        "Los Angeles, CA",
        output_dir=temp_output_dir
    )

    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        assert len(rows) == 500
        assert rows[0]['name'] == 'Business 0'
        assert rows[499]['name'] == 'Business 499'
