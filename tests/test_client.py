import json
from inspect import isawaitable
from pathlib import Path
from typing import AsyncIterator, Awaitable, Iterator, TypeVar, Union

import httpx
import pytest
from snowleopard.client_base import SLClientBase
from snowleopard.error import APIBadRequest, SnowLeopardHTTPError
from snowleopard.models import APIError, FeedbackResponse, ResponseStatus

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


def test_build_path_instance_only():
    assert SLClientBase._build_path("my-instance", None, "retrieve") == "v1/instances/my-instance/retrieve"


def test_build_path_datafile_only():
    assert SLClientBase._build_path(None, "my-datafile", "retrieve") == "datafiles/my-datafile/retrieve"


def test_build_path_instance_takes_precedence():
    # instance_id wins when both are provided
    assert SLClientBase._build_path("my-instance", "my-datafile", "retrieve") == "v1/instances/my-instance/retrieve"


def test_build_path_neither():
    assert SLClientBase._build_path(None, None, "retrieve") == "retrieve"


def test_build_path_feedback_instance():
    assert (
        SLClientBase._build_path("my-instance", None, "feedback")
        == "v1/instances/my-instance/feedback"
    )


def test_build_path_feedback_neither():
    # /feedback is not served by the datafile deployment, so callers always
    # pass datafile_id=None; with no instance_id either, the bare endpoint is used.
    assert SLClientBase._build_path(None, None, "feedback") == "feedback"


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
    assert isinstance(resp, APIError)
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
    # assert isinstance(resp, APIError)
    assert resp.responseStatus == ResponseStatus.INTERNAL_SERVER_ERROR


_empty_query_cases = (
    "",
    "\t",
    )


@pytest.mark.parametrize("user_query", _empty_query_cases)
@pytest.mark.asyncio
async def test_retrieve_with_empty_query(any_client, user_query):
    with pytest.raises(APIBadRequest) as excinfo:
        await maybe_await(any_client.retrieve(user_query=user_query))
    assert excinfo.type is APIBadRequest


@pytest.mark.parametrize("user_query", _empty_query_cases)
@pytest.mark.asyncio
async def test_response_with_empty_query(any_client, user_query):
    with pytest.raises(APIBadRequest) as excinfo:
        [o async for o in maybe_await_iter(any_client.response(user_query=user_query))]
    assert excinfo.type is APIBadRequest


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


@pytest.mark.parametrize("feedback_text", _empty_query_cases)
@pytest.mark.asyncio
async def test_feedback_with_empty_text(any_mock_client, feedback_text):
    def handler(request):
        raise AssertionError("no request should be issued for invalid feedback_text")

    client = any_mock_client(handler)
    with pytest.raises(APIBadRequest) as excinfo:
        await maybe_await(
            client.feedback(feedback_text=feedback_text, instance_id="inst-1")
        )
    assert excinfo.type is APIBadRequest


_missing_instance_id_cases = (None, "", "\t")


@pytest.mark.parametrize("instance_id", _missing_instance_id_cases)
@pytest.mark.asyncio
async def test_feedback_with_missing_instance_id(any_mock_client, feedback_text, instance_id):
    def handler(request):
        raise AssertionError("no request should be issued for a missing instance_id")

    client = any_mock_client(handler)
    with pytest.raises(APIBadRequest) as excinfo:
        await maybe_await(
            client.feedback(feedback_text=feedback_text, instance_id=instance_id)
        )
    assert excinfo.type is APIBadRequest


@pytest.mark.asyncio
async def test_feedback_success(any_mock_client, feedback_text):
    def handler(request):
        return httpx.Response(
            202,
            json={"ok": True, "feedbackId": "fb_123", "gateStatus": "raw"},
        )

    client = any_mock_client(handler)
    resp = await maybe_await(
        client.feedback(feedback_text=feedback_text, instance_id="inst-1")
    )
    assert resp == FeedbackResponse(
        ok=True, feedbackId="fb_123", gateStatus="raw", truncated=False
    )


@pytest.mark.asyncio
async def test_feedback_truncated(any_mock_client, feedback_text):
    def handler(request):
        return httpx.Response(
            202,
            json={
                "ok": True,
                "feedbackId": "fb_123",
                "gateStatus": "raw",
                "truncated": True,
            },
        )

    client = any_mock_client(handler)
    resp = await maybe_await(
        client.feedback(feedback_text=feedback_text, instance_id="inst-1")
    )
    assert resp.truncated is True


@pytest.mark.asyncio
async def test_feedback_sends_optional_fields(any_mock_client, feedback_text):
    captured = {}

    def handler(request):
        captured["body"] = json.loads(request.content)
        return httpx.Response(
            202, json={"ok": True, "feedbackId": "fb_123", "gateStatus": "raw"}
        )

    client = any_mock_client(handler)
    await maybe_await(
        client.feedback(
            feedback_text=feedback_text,
            instance_id="inst-1",
            datasource_id="ds-42",
            schema_id="orders_v2",
        )
    )
    assert captured["body"] == {
        "feedbackText": feedback_text,
        "datasourceId": "ds-42",
        "schemaId": "orders_v2",
    }


@pytest.mark.asyncio
async def test_feedback_omits_absent_optional_fields(any_mock_client, feedback_text):
    captured = {}

    def handler(request):
        captured["body"] = json.loads(request.content)
        return httpx.Response(
            202, json={"ok": True, "feedbackId": "fb_123", "gateStatus": "raw"}
        )

    client = any_mock_client(handler)
    await maybe_await(
        client.feedback(feedback_text=feedback_text, instance_id="inst-1")
    )
    assert captured["body"] == {"feedbackText": feedback_text}


@pytest.mark.asyncio
async def test_feedback_path_with_instance(any_mock_client, feedback_text):
    captured = {}

    def handler(request):
        captured["path"] = request.url.path
        return httpx.Response(
            202, json={"ok": True, "feedbackId": "fb_123", "gateStatus": "raw"}
        )

    client = any_mock_client(handler)
    await maybe_await(
        client.feedback(feedback_text=feedback_text, instance_id="inst-1")
    )
    assert captured["path"] == "/v1/instances/inst-1/feedback"


_feedback_error_cases = (
    (400, {"callId": "call-1", "responseStatus": "BAD_REQUEST", "description": "bad", "__type__": "apiError"}),
    (500, {"callId": "call-2", "responseStatus": "INTERNAL_SERVER_ERROR", "description": "oops", "__type__": "apiError"}),
    (500, {"ok": False, "error": "something went wrong"}),
)


@pytest.mark.parametrize("status_code, body", _feedback_error_cases)
@pytest.mark.asyncio
async def test_feedback_raises_on_error(any_mock_client, feedback_text, status_code, body):
    def handler(request):
        return httpx.Response(status_code, json=body)

    client = any_mock_client(handler)
    with pytest.raises(SnowLeopardHTTPError) as excinfo:
        await maybe_await(
            client.feedback(feedback_text=feedback_text, instance_id="inst-1")
        )
    assert excinfo.value.status_code == status_code
