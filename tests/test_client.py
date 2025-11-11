import pytest
from snowleopard.client import SnowLeopardClient

from conftest import HOW_MANY_SUPERHEROES


@pytest.fixture
def client():
    return SnowLeopardClient("https://dev.snowleopard.ai/")

@pytest.mark.vcr(HOW_MANY_SUPERHEROES)
def test_retrieve_datafile(client, dfid):
    resp = client.retrieve(dfid, "How many superheroes are there?")
    assert "6895" in str(resp.data[0].rows)
