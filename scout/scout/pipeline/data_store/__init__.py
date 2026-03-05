"""DataStore interfaces and implementations."""

from scout.pipeline.data_store.base import DataStore
from scout.pipeline.data_store.sqlite import SQLiteDataStore

__all__ = ["DataStore", "SQLiteDataStore"]
