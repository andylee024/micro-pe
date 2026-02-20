"""CSV export functionality for Scout business data"""

import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


def export_to_csv(
    businesses: List[Dict],
    industry: str,
    location: str,
    output_dir: Optional[Path] = None
) -> Path:
    """
    Export businesses to CSV file with timestamped filename.

    Args:
        businesses: List of business dictionaries containing business data
        industry: Industry type (e.g., "HVAC", "car wash")
        location: Location string (e.g., "Los Angeles, CA")
        output_dir: Optional output directory (defaults to PROJECT_ROOT/outputs)

    Returns:
        Path to the exported CSV file

    Raises:
        IOError: If file cannot be written
        ValueError: If businesses list is empty

    Example:
        >>> businesses = [
        ...     {"name": "Cool Air HVAC", "address": "123 Main St", "phone": "(310) 555-0100"},
        ...     {"name": "Premier Climate", "address": "456 Oak Ave", "phone": "(310) 555-0200"}
        ... ]
        >>> path = export_to_csv(businesses, "HVAC", "Los Angeles, CA")
        >>> print(path)
        /path/to/outputs/hvac_los_angeles_2026-02-19.csv
    """
    if not businesses:
        raise ValueError("Cannot export empty business list")

    # Import here to avoid circular dependency
    from scout.config import OUTPUT_DIR

    if output_dir is None:
        output_dir = OUTPUT_DIR

    # Generate timestamped filename: hvac_los_angeles_2026-02-19.csv
    # Clean up industry and location for filename
    industry_clean = industry.lower().replace(' ', '_').replace(',', '').replace('-', '_')
    location_clean = location.lower().replace(' ', '_').replace(',', '').replace('-', '_')
    timestamp = datetime.now().strftime('%Y-%m-%d')

    filename = f"{industry_clean}_{location_clean}_{timestamp}.csv"
    output_path = output_dir / filename

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Define CSV columns
    fieldnames = ['name', 'address', 'phone', 'website', 'category']

    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()

            # Write each business, ensuring all fields are present
            for business in businesses:
                row = {
                    'name': business.get('name', 'N/A'),
                    'address': business.get('address', 'N/A'),
                    'phone': business.get('phone', 'N/A'),
                    'website': business.get('website', 'N/A'),
                    'category': business.get('category', industry)
                }
                writer.writerow(row)

    except IOError as e:
        raise IOError(f"Failed to write CSV file to {output_path}: {e}")

    return output_path


def format_export_message(
    file_path: Path,
    num_businesses: int,
    fieldnames: Optional[List[str]] = None
) -> str:
    """
    Format a success message for CSV export.

    Args:
        file_path: Path to the exported CSV file
        num_businesses: Number of businesses exported
        fieldnames: Optional list of column names

    Returns:
        Formatted success message string

    Example:
        >>> path = Path("outputs/hvac_los_angeles_2026-02-19.csv")
        >>> message = format_export_message(path, 487)
        >>> print(message)
        ✅ Exported to: outputs/hvac_los_angeles_2026-02-19.csv
           Columns: name, address, phone, website, category
           Rows: 487 businesses
    """
    if fieldnames is None:
        fieldnames = ['name', 'address', 'phone', 'website', 'category']

    columns_str = ', '.join(fieldnames)

    message = (
        f"✅ Exported to: {file_path}\n"
        f"   Columns: {columns_str}\n"
        f"   Rows: {num_businesses} businesses"
    )

    return message
