from scout.pipeline.models.market_dataset import MarketDataset
from scout.pipeline.models.query import Query
from scout.pipeline.runner import Runner


class StubWorkflow:
    def __init__(self):
        self.last_query = None

    def run(self, query: Query) -> MarketDataset:
        self.last_query = query
        return MarketDataset(query=query)


def test_runner_builds_query_and_calls_workflow():
    workflow = StubWorkflow()
    runner = Runner(workflow=workflow)

    dataset = runner.run(
        industry="plumbing", location="Denver, CO", max_results=42, use_cache=False
    )

    assert dataset.query.industry == "plumbing"
    assert dataset.query.location == "Denver, CO"
    assert dataset.query.max_results == 42
    assert dataset.query.use_cache is False
    assert workflow.last_query is dataset.query
