import os

import pytest
from snowleopard.client import SnowLeopardClient

from conftest import HOW_MANY_SUPERHEROES


@pytest.fixture
def token():
    os.environ.get("SNOWLEOPARD_API_KEY", "test_token")

@pytest.fixture
def client(token):
    return SnowLeopardClient(loc="https://dev.snowleopard.ai/", token=token)

@pytest.mark.vcr(HOW_MANY_SUPERHEROES)
def test_retrieve_datafile(client, dfid):
    resp = client.retrieve(dfid, "How many superheroes are there?")
    assert "6895" in str(resp.data[0].rows)
