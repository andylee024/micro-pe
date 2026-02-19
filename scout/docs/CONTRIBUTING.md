# Contributing to Scout

## Code Quality Standards

### Documentation

All public functions and classes must have docstrings following Google style:

```python
def export_to_csv(businesses: List[Dict], industry: str, location: str) -> Path:
    """
    Export businesses to CSV file with timestamped filename.

    Args:
        businesses: List of business dictionaries containing business data
        industry: Industry type (e.g., "HVAC", "car wash")
        location: Location string (e.g., "Los Angeles, CA")

    Returns:
        Path to the exported CSV file

    Raises:
        IOError: If file cannot be written
        ValueError: If businesses list is empty

    Example:
        >>> businesses = [{"name": "Cool Air HVAC", "address": "123 Main St"}]
        >>> path = export_to_csv(businesses, "HVAC", "Los Angeles, CA")
    """
    pass
```

### Error Handling

Always use custom error types and format user-friendly messages:

```python
from scout.utils.errors import (
    APIError, NetworkError, FileIOError,
    format_error_message, handle_api_error
)

try:
    # API call
    response = api.fetch_data()
except Exception as e:
    # Convert to user-friendly error
    api_error = handle_api_error(e, "Google Maps")
    user_message = format_error_message(api_error)
    print(user_message)
```

### Testing

- Write tests for all new functionality
- Aim for >80% code coverage
- Include edge cases and error scenarios
- Use descriptive test names

```python
def test_export_handles_empty_list():
    """Test that exporting empty list raises ValueError"""
    with pytest.raises(ValueError, match="Cannot export empty business list"):
        export_to_csv([], "HVAC", "Los Angeles, CA")
```

## Performance Guidelines

### CSV Export

- Target: <1 second for 500 businesses
- Use streaming writes for large datasets
- Avoid loading entire file into memory

### API Calls

- Always implement caching (90-day TTL)
- Show loading states during network operations
- Timeout after 30 seconds

### Terminal UI

- Refresh rate: 4 FPS (smooth but not excessive)
- Only render visible rows (pagination)
- Update display on state changes only

## Code Formatting

```bash
# Format code
black scout/ tests/

# Lint code
ruff check scout/ tests/
```

## Commit Messages

Follow conventional commits:

```
feat: add CSV export functionality
fix: handle network timeout errors gracefully
docs: update README with terminal UI instructions
test: add integration tests for export pipeline
```

## Pull Request Checklist

- [ ] All tests pass
- [ ] Code formatted with black
- [ ] No lint errors from ruff
- [ ] Docstrings added to public APIs
- [ ] README updated if user-facing changes
- [ ] Manual testing completed
- [ ] Error handling tested
- [ ] Performance validated
