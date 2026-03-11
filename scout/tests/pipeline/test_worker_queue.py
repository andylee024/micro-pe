from datetime import datetime, timezone

from scout.pipeline.data_store.sqlite import SQLiteDataStore
from scout.pipeline.models.market_dataset import MarketDataset
from scout.pipeline.models.query import Query
from scout.pipeline.models.workflow_run import (
    WORKFLOW_STATUS_COMPLETED,
    WORKFLOW_STATUS_FAILED,
    WORKFLOW_STATUS_QUEUED,
    WORKFLOW_STATUS_RUNNING,
)
from scout.pipeline.runner import Runner
from scout.pipeline.worker import WorkflowWorker


def _ts(hour: int, minute: int = 0, second: int = 0) -> datetime:
    return datetime(2026, 3, 11, hour, minute, second, tzinfo=timezone.utc)


def _store(tmp_path):
    return SQLiteDataStore(
        db_path=tmp_path / "queue.db",
        raw_root=tmp_path / "raw",
    )


def test_queue_transitions_queued_running_completed(tmp_path):
    store = _store(tmp_path)
    query = Query(
        industry="hvac",
        location="Austin, TX",
        max_results=25,
        use_cache=True,
        run_id="run-001",
        created_at=_ts(12, 0).isoformat(),
    )

    queued = store.enqueue_workflow(query=query, max_attempts=2)
    assert queued.status == WORKFLOW_STATUS_QUEUED
    assert queued.attempt_count == 0

    running = store.claim_next_workflow(worker_id="worker-a", now=_ts(12, 1))
    assert running is not None
    assert running.run_id == query.run_id
    assert running.status == WORKFLOW_STATUS_RUNNING
    assert running.attempt_count == 1
    assert running.worker_id == "worker-a"
    assert running.claimed_at == _ts(12, 1).isoformat()

    completed = store.complete_workflow(run_id=query.run_id, now=_ts(12, 2))
    assert completed.status == WORKFLOW_STATUS_COMPLETED
    assert completed.finished_at == _ts(12, 2).isoformat()


def test_queue_failure_retries_then_terminal_failure(tmp_path):
    store = _store(tmp_path)
    query = Query(
        industry="plumbing",
        location="Denver, CO",
        run_id="run-002",
        created_at=_ts(13, 0).isoformat(),
    )
    store.enqueue_workflow(query=query, max_attempts=2)

    first_claim = store.claim_next_workflow(worker_id="worker-a", now=_ts(13, 1))
    assert first_claim is not None
    first_fail = store.fail_workflow(
        run_id=query.run_id,
        error_type="RuntimeError",
        error_message="provider timeout",
        error_details={"stage": "fetch", "source": "google_maps"},
        retry_delay_seconds=60,
        now=_ts(13, 2),
    )
    assert first_fail.status == WORKFLOW_STATUS_QUEUED
    assert first_fail.attempt_count == 1
    assert first_fail.available_at == _ts(13, 3).isoformat()
    assert first_fail.error is not None
    assert first_fail.error.error_type == "RuntimeError"
    assert first_fail.error.details["stage"] == "fetch"

    second_claim = store.claim_next_workflow(worker_id="worker-b", now=_ts(13, 3))
    assert second_claim is not None
    assert second_claim.status == WORKFLOW_STATUS_RUNNING
    assert second_claim.attempt_count == 2
    assert second_claim.worker_id == "worker-b"

    second_fail = store.fail_workflow(
        run_id=query.run_id,
        error_type="ValueError",
        error_message="invalid payload",
        error_details={"stage": "normalize", "source": "bizbuysell"},
        retry_delay_seconds=60,
        now=_ts(13, 4),
    )
    assert second_fail.status == WORKFLOW_STATUS_FAILED
    assert second_fail.attempt_count == 2
    assert second_fail.finished_at == _ts(13, 4).isoformat()
    assert second_fail.error is not None
    assert second_fail.error.error_type == "ValueError"
    assert second_fail.error.details["stage"] == "normalize"


class SuccessWorkflow:
    def run(self, query: Query) -> MarketDataset:
        return MarketDataset(query=query)


class FailingWorkflow:
    def run(self, query: Query) -> MarketDataset:
        raise RuntimeError(f"boom:{query.run_id}")


def test_worker_run_once_completes_claimed_run(tmp_path):
    store = _store(tmp_path)
    query = Query(
        industry="electrical",
        location="Phoenix, AZ",
        run_id="run-003",
        created_at=_ts(14, 0).isoformat(),
    )
    store.enqueue_workflow(query=query, max_attempts=2)

    worker = WorkflowWorker(
        data_store=store,
        runner=Runner(workflow=SuccessWorkflow(), data_store=store),
    )
    result = worker.run_once(worker_id="worker-ok", retry_delay_seconds=30, now=_ts(14, 1))

    assert result.claimed is True
    assert result.dataset is not None
    assert result.run is not None
    assert result.run.status == WORKFLOW_STATUS_COMPLETED
    assert result.run.run_id == "run-003"


def test_worker_run_once_requeues_then_fails(tmp_path):
    store = _store(tmp_path)
    query = Query(
        industry="landscaping",
        location="Miami, FL",
        run_id="run-004",
        created_at=_ts(15, 0).isoformat(),
    )
    store.enqueue_workflow(query=query, max_attempts=2)
    worker = WorkflowWorker(
        data_store=store,
        runner=Runner(workflow=FailingWorkflow(), data_store=store),
    )

    first = worker.run_once(worker_id="worker-fail", retry_delay_seconds=0, now=_ts(15, 1))
    assert first.claimed is True
    assert first.dataset is None
    assert first.run is not None
    assert first.run.status == WORKFLOW_STATUS_QUEUED
    assert first.run.error is not None
    assert first.run.error.error_type == "RuntimeError"
    assert "worker-fail" in str(first.run.error.details.get("worker_id"))

    second = worker.run_once(worker_id="worker-fail", retry_delay_seconds=0, now=_ts(15, 2))
    assert second.claimed is True
    assert second.dataset is None
    assert second.run is not None
    assert second.run.status == WORKFLOW_STATUS_FAILED
    assert second.run.attempt_count == 2
