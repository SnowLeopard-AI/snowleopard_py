import pytest

from .conftest import HOW_MANY_SUPERHEROES


@pytest.mark.vcr(HOW_MANY_SUPERHEROES)
def test_retrieve_datafile(client, superheroes):
    resp = client.retrieve(superheroes, "How many superheroes are there?")
    assert "6895" in str(resp.data[0].rows)
