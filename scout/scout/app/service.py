"""Service boundary for persisted search runs and curated lead operations."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import asdict
from pathlib import Path

from scout.app.models import LeadRecord, SearchExecution
from scout.app.store import AppStateStore
from scout.pipeline.data_store.sqlite import SQLiteDataStore
from scout.pipeline.runner import Runner


class ScoutAppService:
    """Application service on top of pipeline execution and canonical storage."""

    def __init__(
        self,
        *,
        runner: Runner | None = None,
        store: AppStateStore | None = None,
        db_path: str | Path = "outputs/pipeline/canonical.db",
        raw_root: str | Path = "outputs/pipeline/raw",
    ) -> None:
        self._owns_runner_datastore = runner is None
        if runner is None:
            data_store = SQLiteDataStore(db_path=db_path, raw_root=raw_root)
            runner = Runner(data_store=data_store)
        self.runner = runner

        resolved_db_path = self._resolve_db_path(fallback=db_path)
        self.store = store or AppStateStore(db_path=resolved_db_path)

    def close(self) -> None:
        self.store.close()
        if not self._owns_runner_datastore:
            return
        data_store = getattr(self.runner, "data_store", None)
        close_fn = getattr(data_store, "close", None)
        if callable(close_fn):
            close_fn()

    def run_search(
        self,
        *,
        query_text: str,
        industry: str,
        location: str,
        max_results: int = 100,
        use_cache: bool = True,
    ) -> SearchExecution:
        dataset = self.runner.run(
            industry=industry,
            location=location,
            max_results=max_results,
            use_cache=use_cache,
        )

        search = self.store.upsert_search(
            query_text=query_text,
            industry=industry,
            location=location,
            max_results=max_results,
            use_cache=use_cache,
        )
        search_run = self.store.upsert_search_run(
            run_id=dataset.query.run_id,
            search_id=search.search_id,
            status="completed",
            created_at=dataset.query.created_at,
            completed_at=dataset.created_at,
            business_count=len(dataset.businesses),
            listing_count=len(dataset.listings),
            coverage_json=json.dumps([asdict(item) for item in dataset.coverage], sort_keys=True),
        )

        business_ids: list[int] = []
        for business in dataset.businesses:
            business_id = self.store.find_business_id(business)
            if business_id is not None:
                business_ids.append(business_id)
        self.store.attach_run_businesses(search_run.run_id, business_ids)

        listing_ids = [
            listing.id for listing in dataset.listings if self.store.listing_exists(listing.id)
        ]
        self.store.attach_run_listings(search_run.run_id, listing_ids)
        return SearchExecution(search=search, search_run=search_run, dataset=dataset)

    def list_leads(
        self,
        *,
        search_id: str | None = None,
        saved_only: bool = False,
        limit: int = 200,
    ) -> list[LeadRecord]:
        resolved_search_id = self._resolve_search_id(search_id)
        return self.store.list_leads(
            search_id=resolved_search_id,
            saved_only=saved_only,
            limit=limit,
        )

    def save_lead(
        self,
        *,
        lead_id: str,
        search_id: str | None = None,
        note: str = "",
        summary: str = "",
    ) -> LeadRecord:
        resolved_search_id = self._resolve_search_id(search_id)
        return self.store.save_lead(
            lead_id=lead_id,
            search_id=resolved_search_id,
            note=note,
            summary=summary,
        )

    def remove_lead(self, *, lead_id: str) -> bool:
        return self.store.remove_lead(lead_id)

    def list_saved_leads(
        self, *, search_id: str | None = None, limit: int = 200
    ) -> list[LeadRecord]:
        resolved_search_id = self._resolve_search_id(search_id) if search_id is not None else None
        return self.store.list_saved_leads(search_id=resolved_search_id, limit=limit)

    def export_saved_leads_csv(self, *, search_id: str | None = None) -> str:
        rows = self.list_saved_leads(search_id=search_id)
        fieldnames = [
            "lead_id",
            "lead_type",
            "name",
            "industry",
            "location",
            "state",
            "source",
            "source_record_id",
            "phone",
            "website",
            "url",
            "summary",
            "note",
            "search_id",
            "saved_at",
        ]
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for lead in rows:
            writer.writerow(
                {
                    "lead_id": lead.lead_id,
                    "lead_type": lead.lead_type,
                    "name": lead.name,
                    "industry": lead.industry,
                    "location": lead.location,
                    "state": lead.state,
                    "source": lead.source,
                    "source_record_id": lead.source_record_id,
                    "phone": lead.phone,
                    "website": lead.website,
                    "url": lead.url,
                    "summary": lead.summary,
                    "note": lead.note,
                    "search_id": lead.search_id,
                    "saved_at": lead.saved_at,
                }
            )
        return stream.getvalue()

    def _resolve_search_id(self, search_id: str | None) -> str:
        if search_id is not None and search_id.strip():
            return search_id.strip()
        latest = self.store.get_latest_search_id()
        if latest is None:
            raise ValueError("No persisted search state exists yet.")
        return latest

    def _resolve_db_path(self, *, fallback: str | Path) -> Path:
        data_store = getattr(self.runner, "data_store", None)
        if isinstance(data_store, SQLiteDataStore):
            return Path(data_store.db_path)
        db_path = getattr(data_store, "db_path", None)
        if db_path:
            return Path(str(db_path))
        return Path(fallback)
