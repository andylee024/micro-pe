from scout.pipeline.data_sources.base import DataSource, NormalizedBatch
from scout.pipeline.data_store.base import DataStore
from scout.pipeline.models.business import Business
from scout.pipeline.models.listing import Listing
from scout.pipeline.models.query import Query
from scout.pipeline.workflow import Workflow


class MemoryStore(DataStore):
    def __init__(self):
        self.raw = {}
        self.businesses = []
        self.listings = []
        self.history_runs = []

    def persist_raw(self, run_id: str, source: str, payload: dict[str, object]) -> str:
        key = f"{run_id}:{source}"
        self.raw[key] = payload
        return key

    def upsert_businesses(self, businesses: list[Business]) -> int:
        self.businesses.extend(businesses)
        return len(businesses)

    def upsert_listings(self, listings: list[Listing]) -> int:
        self.listings.extend(listings)
        return len(listings)

    def record_business_history(self, query: Query, businesses: list[Business]) -> None:
        self.history_runs.append((query, list(businesses)))


class GoodSource(DataSource):
    name = "good"

    def fetch(self, query: Query) -> dict[str, object]:
        return {"ok": True, "query": query.industry}

    def normalize(self, raw: dict[str, object], query: Query) -> NormalizedBatch:
        return NormalizedBatch(
            businesses=[Business(name="Acme", source=self.name)],
            listings=[
                Listing(
                    source=self.name,
                    source_id="1",
                    url="https://example.com/1",
                    name="Acme Listing",
                    industry=query.industry,
                    location=query.location,
                )
            ],
            signals={"ok": raw["ok"]},
        )


class BadSource(DataSource):
    name = "bad"

    def fetch(self, query: Query) -> dict[str, object]:
        raise RuntimeError("boom")

    def normalize(self, raw: dict[str, object], query: Query) -> NormalizedBatch:
        raise NotImplementedError


def test_workflow_fail_soft_and_collects_coverage():
    store = MemoryStore()
    workflow = Workflow(data_sources=[GoodSource(), BadSource()], data_store=store)

    dataset = workflow.run(Query(industry="hvac", location="Austin, TX", max_results=10))

    assert len(dataset.businesses) == 1
    assert len(dataset.listings) == 1
    assert dataset.signals["good"]["ok"] is True

    by_source = {item.source: item for item in dataset.coverage}
    assert by_source["good"].status == "success"
    assert by_source["good"].records == 2
    assert by_source["bad"].status == "failed"
    assert "boom" in by_source["bad"].error

    # Raw persisted only for successful fetch.
    assert any(key.endswith(":good") for key in store.raw)
    assert not any(key.endswith(":bad") for key in store.raw)

    assert len(store.history_runs) == 1
    history_query, history_businesses = store.history_runs[0]
    assert history_query is dataset.query
    assert len(history_businesses) == 1
    assert history_businesses[0].name == "Acme"
