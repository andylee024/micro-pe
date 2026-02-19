"""Error handling utilities for Scout"""

from typing import Optional, Callable, Any
from functools import wraps
import traceback
import sys


class ScoutError(Exception):
    """Base exception for Scout errors"""
    pass


class APIError(ScoutError):
    """Error related to API calls (Google Maps, etc.)"""
    def __init__(self, message: str, api_name: str = "API", original_error: Optional[Exception] = None):
        self.api_name = api_name
        self.original_error = original_error
        super().__init__(message)


class NetworkError(ScoutError):
    """Error related to network connectivity"""
    pass


class FileIOError(ScoutError):
    """Error related to file I/O operations"""
    pass


class ConfigurationError(ScoutError):
    """Error related to configuration or setup"""
    pass


class ValidationError(ScoutError):
    """Error related to data validation"""
    pass


def format_error_message(error: Exception, show_details: bool = False) -> str:
    """
    Format an error message for user display.

    Args:
        error: The exception to format
        show_details: Whether to include technical details

    Returns:
        Formatted error message string

    Example:
        >>> error = APIError("Connection failed", api_name="Google Maps")
        >>> print(format_error_message(error))
        ❌ Error: Connection failed
           Please check your GOOGLE_MAPS_API_KEY in .env file
    """
    if isinstance(error, APIError):
        message = f"❌ Error: {str(error)}"
        if error.api_name == "Google Maps":
            message += (
                "\n   Please check your GOOGLE_MAPS_API_KEY in .env file"
                "\n   Run: scout research --help for more info"
            )
        elif show_details and error.original_error:
            message += f"\n   Details: {str(error.original_error)}"

    elif isinstance(error, NetworkError):
        message = (
            f"❌ Error: {str(error)}"
            "\n   Please check your internet connection and try again"
        )

    elif isinstance(error, FileIOError):
        message = (
            f"❌ Error: {str(error)}"
            "\n   Please check file permissions and disk space"
        )

    elif isinstance(error, ConfigurationError):
        message = (
            f"❌ Error: {str(error)}"
            "\n   Please check your configuration in .env file"
        )

    elif isinstance(error, ValidationError):
        message = f"❌ Error: {str(error)}"

    else:
        # Generic error
        message = f"❌ Error: {str(error)}"
        if show_details:
            message += f"\n   Type: {type(error).__name__}"

    return message


def safe_execute(func: Callable, *args, error_message: str = "Operation failed", **kwargs) -> tuple[bool, Any]:
    """
    Safely execute a function and return (success, result).

    Args:
        func: Function to execute
        *args: Positional arguments for the function
        error_message: Custom error message prefix
        **kwargs: Keyword arguments for the function

    Returns:
        Tuple of (success: bool, result: Any)
        If success is False, result contains the error message

    Example:
        >>> def risky_operation():
        ...     return 42
        >>> success, result = safe_execute(risky_operation)
        >>> if success:
        ...     print(f"Result: {result}")
    """
    try:
        result = func(*args, **kwargs)
        return True, result
    except Exception as e:
        error_msg = format_error_message(e)
        return False, f"{error_message}: {error_msg}"


def handle_errors(default_return=None, show_traceback: bool = False):
    """
    Decorator to handle errors gracefully in functions.

    Args:
        default_return: Value to return on error
        show_traceback: Whether to print traceback to stderr

    Example:
        >>> @handle_errors(default_return=[])
        ... def fetch_data():
        ...     return get_api_data()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = format_error_message(e, show_details=True)
                print(error_msg, file=sys.stderr)

                if show_traceback:
                    traceback.print_exc(file=sys.stderr)

                return default_return

        return wrapper
    return decorator


def validate_api_key(api_key: Optional[str], api_name: str) -> None:
    """
    Validate that an API key is present and non-empty.

    Args:
        api_key: API key to validate
        api_name: Name of the API for error message

    Raises:
        ConfigurationError: If API key is missing or empty
    """
    if not api_key or not api_key.strip():
        raise ConfigurationError(
            f"{api_name} API key is missing or empty. "
            f"Please set it in your .env file."
        )


def validate_location(location: str) -> None:
    """
    Validate that a location string is reasonable.

    Args:
        location: Location string to validate

    Raises:
        ValidationError: If location is invalid
    """
    if not location or not location.strip():
        raise ValidationError("Location cannot be empty")

    if len(location.strip()) < 2:
        raise ValidationError("Location must be at least 2 characters")


def validate_industry(industry: str) -> None:
    """
    Validate that an industry string is reasonable.

    Args:
        industry: Industry string to validate

    Raises:
        ValidationError: If industry is invalid
    """
    if not industry or not industry.strip():
        raise ValidationError("Industry cannot be empty")

    if len(industry.strip()) < 2:
        raise ValidationError("Industry must be at least 2 characters")


def handle_api_error(error: Exception, api_name: str) -> APIError:
    """
    Convert a generic exception to an APIError with helpful context.

    Args:
        error: Original exception
        api_name: Name of the API that failed

    Returns:
        APIError with context
    """
    error_str = str(error).lower()

    if "timeout" in error_str:
        message = f"{api_name} request timed out"
    elif "connection" in error_str or "network" in error_str:
        message = f"Could not connect to {api_name}"
    elif "authentication" in error_str or "unauthorized" in error_str:
        message = f"{api_name} authentication failed - check your API key"
    elif "rate limit" in error_str or "quota" in error_str:
        message = f"{api_name} rate limit exceeded - try again later"
    else:
        message = f"{api_name} request failed: {str(error)}"

    return APIError(message, api_name=api_name, original_error=error)


def handle_file_error(error: Exception, file_path: str, operation: str = "access") -> FileIOError:
    """
    Convert a generic file exception to a FileIOError with context.

    Args:
        error: Original exception
        file_path: Path to the file
        operation: Operation being performed (read, write, delete, etc.)

    Returns:
        FileIOError with context
    """
    error_str = str(error).lower()

    if "permission" in error_str or "denied" in error_str:
        message = f"Permission denied to {operation} file: {file_path}"
    elif "not found" in error_str or "no such file" in error_str:
        message = f"File not found: {file_path}"
    elif "disk" in error_str or "space" in error_str:
        message = f"Insufficient disk space to {operation} file: {file_path}"
    else:
        message = f"Failed to {operation} file {file_path}: {str(error)}"

    return FileIOError(message)
