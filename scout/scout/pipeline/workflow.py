"""Workflow orchestration."""

from __future__ import annotations

import time

from scout.pipeline.data_sources.base import DataSource
from scout.pipeline.data_store.base import DataStore
from scout.pipeline.models.business import Business
from scout.pipeline.models.listing import Listing
from scout.pipeline.models.market_dataset import Coverage, MarketDataset
from scout.pipeline.models.query import Query


class Workflow:
    """Runs a stage-based ETL flow across configured data sources."""

    def __init__(self, data_sources: list[DataSource], data_store: DataStore) -> None:
        self.data_sources = data_sources
        self.data_store = data_store

    def run(self, query: Query) -> MarketDataset:
        all_businesses: list[Business] = []
        all_listings: list[Listing] = []
        signals: dict[str, object] = {}
        coverage: list[Coverage] = []
        run_diff = None

        for source in self.data_sources:
            started = time.perf_counter()
            try:
                raw = source.fetch(query)
                self.data_store.persist_raw(query.run_id, source.name, raw)

                batch = source.normalize(raw, query)
                businesses = [record for record in batch.businesses if record.name]
                listings = [record for record in batch.listings if record.name]

                self.data_store.upsert_businesses(businesses)
                self.data_store.upsert_listings(listings)

                all_businesses.extend(businesses)
                all_listings.extend(listings)
                signals[source.name] = batch.signals

                status = "empty" if not businesses and not listings else "success"
                coverage.append(
                    Coverage(
                        source=source.name,
                        status=status,
                        records=len(businesses) + len(listings),
                        duration_ms=int((time.perf_counter() - started) * 1000),
                    )
                )
            except Exception as exc:  # noqa: BLE001
                coverage.append(
                    Coverage(
                        source=source.name,
                        status="failed",
                        records=0,
                        error=str(exc),
                        duration_ms=int((time.perf_counter() - started) * 1000),
                    )
                )

        record_business_history = getattr(self.data_store, "record_business_history", None)
        if callable(record_business_history):
            record_business_history(query, all_businesses)

        record_run = getattr(self.data_store, "record_run", None)
        if callable(record_run):
            run_diff = record_run(query=query, businesses=all_businesses, listings=all_listings)

        return MarketDataset(
            query=query,
            businesses=all_businesses,
            listings=all_listings,
            signals=signals,
            coverage=coverage,
            run_diff=run_diff,
        )
