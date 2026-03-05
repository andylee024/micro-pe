"""Compatibility shim for legacy imports.

Canonical model lives at scout.pipeline.models.listing.Listing.
"""

from scout.pipeline.models.listing import Listing

__all__ = ["Listing"]
