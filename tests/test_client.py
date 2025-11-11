from inspect import isawaitable
from typing import Awaitable, TypeVar

import pytest

from .conftest import HOW_MANY_SUPERHEROES

T = TypeVar("T")


async def maybe_await(obj: T | Awaitable[T]) -> T:
    if isawaitable(obj):
        obj = await obj
    return obj


@pytest.mark.vcr(HOW_MANY_SUPERHEROES)
@pytest.mark.asyncio
async def test_retrieve_with_success(
        any_client,
        superheroes,
        how_many_superheroes_q
):
    resp = await maybe_await(any_client.retrieve(superheroes, how_many_superheroes_q))
    assert "6895" in str(resp.data[0].rows)
