from inspect import isawaitable
from pathlib import Path
from typing import Awaitable, TypeVar

import pytest
from snowleopard.errors import NotInSchema, APIError

from .conftest import HOW_MANY_SUPERHEROES, CASSETTES_DIR

T = TypeVar("T")


async def maybe_await(obj: T | Awaitable[T]) -> T:
    if isawaitable(obj):
        obj = await obj
    return obj


# explicitly set the default cassette loc since parameterized tests would create 2 recordings rather than 1
def cassette(cassette_loc: str | Path):
    return lambda fn: (
        pytest.mark.default_cassette(str(cassette_loc))(
            pytest.mark.vcr(
                pytest.mark.asyncio(fn)
            )
        )
    )


@cassette(HOW_MANY_SUPERHEROES)
async def test_retrieve_with_success(
        any_client,
        superheroes,
        how_many_superheroes_q
):
    resp = await maybe_await(any_client.retrieve(superheroes, how_many_superheroes_q))
    assert "6895" in str(resp.data[0].rows)


@cassette(CASSETTES_DIR / "not_in_schema.yaml")
async def test_retrieve_not_in_schema(any_client, superheroes):
    with pytest.raises(NotInSchema) as e:
        await maybe_await(any_client.retrieve(superheroes, "What language is the most spoken amongst superheroes?"))
    assert str(e.value) == "The data doesn't exist in the schema to answer this question. Please review the schema and ask a different question."


@cassette(CASSETTES_DIR / "query_error.yaml")
async def test_retrieve_with_bad_query(any_client, superheroes):
    with pytest.raises(APIError) as e:
        await maybe_await(any_client.retrieve(superheroes, "What language is the most spoken amongst superheroes?"))
    assert e.value.response.json()["responseStatus"] == "INTERNAL_SERVER_ERROR"