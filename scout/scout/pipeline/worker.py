"""Worker entrypoint for queued workflow execution."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from scout.pipeline.data_store.sqlite import SQLiteDataStore
from scout.pipeline.models.market_dataset import MarketDataset
from scout.pipeline.models.query import Query
from scout.pipeline.models.workflow_run import WorkflowRun
from scout.pipeline.runner import Runner


@dataclass(frozen=True)
class WorkerRunResult:
    """Outcome of one worker tick."""

    claimed: bool
    run: WorkflowRun | None = None
    dataset: MarketDataset | None = None


class WorkflowWorker:
    """Claims one queued workflow run and executes it."""

    def __init__(self, data_store: SQLiteDataStore, runner: Runner | None = None) -> None:
        self.data_store = data_store
        self.runner = runner or Runner(data_store=data_store)

    def run_once(
        self,
        worker_id: str,
        retry_delay_seconds: int = 0,
        now: datetime | str | None = None,
    ) -> WorkerRunResult:
        claimed = self.data_store.claim_next_workflow(worker_id=worker_id, now=now)
        if claimed is None:
            return WorkerRunResult(claimed=False)

        query = Query(
            industry=claimed.industry,
            location=claimed.location,
            max_results=claimed.max_results,
            use_cache=claimed.use_cache,
            run_id=claimed.run_id,
            created_at=claimed.created_at,
        )

        try:
            dataset = self.runner.run_query(query)
        except Exception as exc:  # noqa: BLE001
            run = self.data_store.fail_workflow(
                run_id=claimed.run_id,
                error_type=exc.__class__.__name__,
                error_message=str(exc),
                error_details={
                    "worker_id": worker_id,
                    "retry_delay_seconds": retry_delay_seconds,
                },
                retry_delay_seconds=retry_delay_seconds,
                now=now,
            )
            return WorkerRunResult(claimed=True, run=run, dataset=None)

        run = self.data_store.complete_workflow(run_id=claimed.run_id, now=now)
        return WorkerRunResult(claimed=True, run=run, dataset=dataset)
