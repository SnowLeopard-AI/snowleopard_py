import json

import httpx
import pytest
from snowleopard.cli import main
from snowleopard.client import SnowLeopardClient

from .conftest import (
    HOW_MANY_SUPERHEROES,
    HOW_MANY_SUPERHEROES_RESPONSE,
    HOW_MANY_SUPERHEROES_NO_DFID,
)


_empty_query_cases = (
    "",
    "\t",
    )


def test_main_no_args(capsys):
    """Test that main function prints help when no command is given."""
    try:
        main(["-h"])
    except SystemExit as e:
        assert e.code == 0

    captured = capsys.readouterr()
    assert "usage:" in captured.out


@pytest.mark.parametrize("user_query", _empty_query_cases)
def test_retrieve_command_blank_user_query(capsys, loc, superheroes, api_key, user_query):
    try:
        main(
            [
                "-l",
                loc,
                "-a",
                api_key,
                "retrieve",
                "-df",
                superheroes,
                user_query,
            ]
        )
    except SystemExit as e:
        assert e.code == 1

    captured = capsys.readouterr()
    assert "error:" in captured.err


@pytest.mark.default_cassette(HOW_MANY_SUPERHEROES)
@pytest.mark.vcr
def test_retrieve_command(capsys, loc, superheroes, api_key, how_many_superheroes_q):
    main(
        [
            "-l",
            loc,
            "-a",
            api_key,
            "retrieve",
            "-df",
            superheroes,
            how_many_superheroes_q,
        ]
    )
    stdout = capsys.readouterr().out
    assert "6895" in stdout
    assert "callId" in json.loads(stdout)


@pytest.mark.default_cassette(HOW_MANY_SUPERHEROES_NO_DFID)
@pytest.mark.vcr
def test_retrieve_command_no_dfid(capsys, api_key, how_many_superheroes_q):
    main(
        [
            "-l",
            "https://localhost:8000",
            "-a",
            api_key,
            "retrieve",
            how_many_superheroes_q,
        ]
    )
    stdout = capsys.readouterr().out
    assert "6895" in stdout
    assert "callId" in json.loads(stdout)


@pytest.mark.parametrize("user_query", _empty_query_cases)
def test_response_command_blank_user_query(capsys, loc, superheroes, api_key, user_query):
    try:
        main(
            [
                "-l",
                loc,
                "-a",
                api_key,
                "response",
                "-df",
                superheroes,
                user_query,
            ]
        )
    except SystemExit as e:
        assert e.code == 1

    captured = capsys.readouterr()
    assert "error:" in captured.err


@pytest.mark.default_cassette(HOW_MANY_SUPERHEROES_RESPONSE)
@pytest.mark.vcr
def test_response_command(capsys, loc, superheroes, api_key, how_many_superheroes_q):
    main(
        [
            "-l",
            loc,
            "-a",
            api_key,
            "response",
            "--datafile",
            superheroes,
            how_many_superheroes_q,
        ]
    )
    stdout = capsys.readouterr().out
    assert "6895" in stdout
    for line in stdout.splitlines():
        assert "callId" in json.loads(line)


def _mock_client_class(handler):
    """Build a SnowLeopardClient subclass whose transport is an httpx.MockTransport
    wired to the given handler, for use as a monkeypatch replacement of
    snowleopard.cli.SnowLeopardClient. There is no live /feedback service to
    record a cassette against, so CLI feedback tests use a mock transport instead.
    """

    class MockClient(SnowLeopardClient):
        def __init__(self, api_key=None, timeout=None, loc=None):
            super().__init__(api_key=api_key, timeout=timeout, loc=loc)
            self.client = httpx.Client(
                base_url=loc,
                headers=self.client.headers,
                transport=httpx.MockTransport(handler),
            )

    return MockClient


@pytest.mark.parametrize("feedback_text", _empty_query_cases)
def test_feedback_command_blank_text(capsys, loc, api_key, feedback_text):
    try:
        main(["-l", loc, "-a", api_key, "feedback", feedback_text])
    except SystemExit as e:
        assert e.code == 1

    captured = capsys.readouterr()
    assert "error:" in captured.err


def test_feedback_command(monkeypatch, capsys, loc, api_key):
    captured = {}

    def handler(request):
        captured["url"] = str(request.url)
        captured["body"] = json.loads(request.content)
        return httpx.Response(
            202, json={"ok": True, "feedbackId": "fb_123", "gateStatus": "raw"}
        )

    monkeypatch.setattr("snowleopard.cli.SnowLeopardClient", _mock_client_class(handler))

    main(
        [
            "-l",
            loc,
            "-a",
            api_key,
            "feedback",
            "-i",
            "inst-1",
            "-ds",
            "ds-42",
            "-s",
            "orders_v2",
            "the revenue totals looked wrong",
        ]
    )
    stdout = capsys.readouterr().out
    assert json.loads(stdout) == {
        "ok": True,
        "feedbackId": "fb_123",
        "gateStatus": "raw",
        "truncated": False,
    }
    assert captured["url"].endswith("/v1/instances/inst-1/feedback")
    assert captured["body"] == {
        "feedbackText": "the revenue totals looked wrong",
        "datasourceId": "ds-42",
        "schemaId": "orders_v2",
    }


def test_feedback_command_http_error(monkeypatch, capsys, loc, api_key):
    def handler(request):
        return httpx.Response(500, json={"ok": False, "error": "something broke"})

    monkeypatch.setattr("snowleopard.cli.SnowLeopardClient", _mock_client_class(handler))

    try:
        main(["-l", loc, "-a", api_key, "feedback", "some feedback"])
    except SystemExit as e:
        assert e.code == 1

    captured = capsys.readouterr()
    assert "error:" in captured.err
