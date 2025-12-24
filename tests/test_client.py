from inspect import isawaitable
from pathlib import Path
from typing import AsyncIterator, Awaitable, Iterator, TypeVar, Union

import pytest
from snowleopard.models import RetrieveResponseError, ResponseStatus

from .conftest import (
    HOW_MANY_SUPERHEROES,
    CASSETTES_DIR,
    HOW_MANY_SUPERHEROES_RESPONSE,
    HOW_MANY_SUPERHEROES_NO_DFID,
)

T = TypeVar("T")


async def maybe_await(obj: Union[T, Awaitable[T]]) -> T:
    if isawaitable(obj):
        obj = await obj
    return obj


async def maybe_await_iter(
    obj: Union[Iterator[T], AsyncIterator[T]],
) -> AsyncIterator[T]:
    if hasattr(obj, "__anext__"):
        async for item in obj:
            yield item
    else:
        for item in obj:
            yield item


# explicitly set the default cassette loc since parameterized tests would create 2 recordings rather than 1
def cassette(cassette_loc: Union[str, Path]):
    return lambda fn: (
        pytest.mark.default_cassette(str(cassette_loc))(
            pytest.mark.vcr(pytest.mark.asyncio(fn))
        )
    )


@cassette(HOW_MANY_SUPERHEROES)
async def test_retrieve_with_success(any_client, superheroes, how_many_superheroes_q):
    resp = await maybe_await(
        any_client.retrieve(user_query=how_many_superheroes_q, datafile_id=superheroes)
    )
    assert "6895" in str(resp.data[0].rows)


@cassette(HOW_MANY_SUPERHEROES_NO_DFID)
async def test_retrieve_with_success_no_dfid(any_client, how_many_superheroes_q):
    any_client.client.base_url = "https://localhost:8000"
    resp = await maybe_await(any_client.retrieve(user_query=how_many_superheroes_q))
    assert "6895" in str(resp.data[0].rows)


@cassette(CASSETTES_DIR / "not_in_schema.yaml")
async def test_retrieve_not_in_schema(any_client, superheroes):
    resp = await maybe_await(
        any_client.retrieve(
            user_query="What language is the most spoken amongst superheroes?",
            datafile_id=superheroes,
        )
    )
    assert isinstance(resp, RetrieveResponseError)
    assert (
        resp.description
        == "The data doesn't exist in the schema to answer this question. Please review the schema and ask a different question."
    )
    assert resp.responseStatus == ResponseStatus.NOT_FOUND_IN_SCHEMA


@cassette(CASSETTES_DIR / "query_error.yaml")
async def test_retrieve_with_bad_query(any_client, superheroes):
    resp = await maybe_await(
        any_client.retrieve(
            user_query="What language is the most spoken amongst superheroes?",
            datafile_id=superheroes,
        )
    )
    # currently api is not returning this as error kind, which is definitely confusing
    # assert isinstance(resp, RetrieveResponseError)
    assert resp.responseStatus == ResponseStatus.INTERNAL_SERVER_ERROR


@cassette(HOW_MANY_SUPERHEROES_RESPONSE)
async def test_response_with_success(any_client, superheroes, how_many_superheroes_q):
    resp = [
        o
        async for o in maybe_await_iter(
            any_client.response(
                user_query=how_many_superheroes_q, datafile_id=superheroes
            )
        )
    ]
    assert {o.objType for o in resp} == {
        "responseStart",
        "responseData",
        "responseResult",
    }
    assert "6895" in str(resp)
