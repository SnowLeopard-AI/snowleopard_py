import pytest

from .conftest import HOW_MANY_SUPERHEROES


@pytest.mark.vcr(HOW_MANY_SUPERHEROES)
def test_retrieve_datafile(client, superheroes, how_many_superheroes_q):
    resp = client.retrieve(superheroes, how_many_superheroes_q)
    assert "6895" in str(resp.data[0].rows)


@pytest.mark.vcr(HOW_MANY_SUPERHEROES)
@pytest.mark.asyncio
async def test_async_retrieve_datafile(async_client, superheroes, how_many_superheroes_q):
    resp = await async_client.retrieve(superheroes, how_many_superheroes_q)
    assert "6895" in str(resp.data[0].rows)