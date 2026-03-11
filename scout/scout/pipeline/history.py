"""Operator-facing history and diff service."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from scout.pipeline.data_store.sqlite import SQLiteDataStore
from scout.pipeline.models.history import RunDiffItem, RunDiffView, RunHistoryEntry


class HistoryService:
    """Reads canonical run/diff state and formats history payloads."""

    def __init__(self, db_path: str | Path = "outputs/pipeline/canonical.db") -> None:
        self._store = SQLiteDataStore(db_path=db_path)

    def close(self) -> None:
        self._store.close()

    def list_runs(
        self,
        *,
        limit: int = 10,
        industry: str | None = None,
        location: str | None = None,
    ) -> list[RunHistoryEntry]:
        rows = self._store.list_search_runs(limit=limit, industry=industry, location=location)
        results: list[RunHistoryEntry] = []
        for row in rows:
            results.append(
                RunHistoryEntry(
                    run_id=str(row["run_id"]),
                    created_at=str(row["created_at"]),
                    industry=str(row["industry"]),
                    location=str(row["location"]),
                    business_count=int(row["business_count"]),
                    listing_count=int(row["listing_count"]),
                    previous_run_id=_optional_text(row["previous_run_id"]),
                    added_businesses=_int_or_zero(row["added_businesses"]),
                    removed_businesses=_int_or_zero(row["removed_businesses"]),
                    added_listings=_int_or_zero(row["added_listings"]),
                    removed_listings=_int_or_zero(row["removed_listings"]),
                )
            )
        return results

    def get_diff(self, *, run_id: str) -> RunDiffView:
        summary = self._store.get_run_diff(run_id)
        if summary is None:
            raise ValueError(f"run_id not found: {run_id}")

        item_rows = self._store.get_run_diff_items(run_id)
        items = [
            RunDiffItem(
                item_type=str(row["item_type"]),
                change_type=str(row["change_type"]),
                item_key=str(row["item_key"]),
                source=str(row["source"]),
                name=str(row["name"]),
                location=str(row["location"] or ""),
                state=str(row["state"] or ""),
            )
            for row in item_rows
        ]
        return RunDiffView(
            run_id=str(summary["run_id"]),
            created_at=str(summary["created_at"]),
            industry=str(summary["industry"]),
            location=str(summary["location"]),
            previous_run_id=_optional_text(summary["previous_run_id"]),
            added_businesses=_int_or_zero(summary["added_businesses"]),
            removed_businesses=_int_or_zero(summary["removed_businesses"]),
            added_listings=_int_or_zero(summary["added_listings"]),
            removed_listings=_int_or_zero(summary["removed_listings"]),
            items=items,
        )

    def export_diff(
        self,
        *,
        run_id: str,
        output_path: str | Path,
        fmt: str = "csv",
    ) -> Path:
        view = self.get_diff(run_id=run_id)
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        fmt_normalized = fmt.strip().lower()
        if fmt_normalized == "csv":
            self._write_diff_csv(output=output, view=view)
        elif fmt_normalized == "json":
            self._write_diff_json(output=output, view=view)
        else:
            raise ValueError(f"unsupported export format: {fmt}")
        return output

    def _write_diff_csv(self, *, output: Path, view: RunDiffView) -> None:
        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "run_id",
                    "previous_run_id",
                    "item_type",
                    "change_type",
                    "item_key",
                    "source",
                    "name",
                    "location",
                    "state",
                ],
            )
            writer.writeheader()
            for item in view.items:
                writer.writerow(
                    {
                        "run_id": view.run_id,
                        "previous_run_id": view.previous_run_id or "",
                        "item_type": item.item_type,
                        "change_type": item.change_type,
                        "item_key": item.item_key,
                        "source": item.source,
                        "name": item.name,
                        "location": item.location,
                        "state": item.state,
                    }
                )

    def _write_diff_json(self, *, output: Path, view: RunDiffView) -> None:
        payload: dict[str, Any] = {
            "run_id": view.run_id,
            "created_at": view.created_at,
            "industry": view.industry,
            "location": view.location,
            "previous_run_id": view.previous_run_id,
            "added_businesses": view.added_businesses,
            "removed_businesses": view.removed_businesses,
            "added_listings": view.added_listings,
            "removed_listings": view.removed_listings,
            "items": [
                {
                    "item_type": item.item_type,
                    "change_type": item.change_type,
                    "item_key": item.item_key,
                    "source": item.source,
                    "name": item.name,
                    "location": item.location,
                    "state": item.state,
                }
                for item in view.items
            ],
        }
        output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _int_or_zero(value: object) -> int:
    if value is None:
        return 0
    return int(value)
