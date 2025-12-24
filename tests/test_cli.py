import json

import pytest
from snowleopard.cli import main

from .conftest import (
    HOW_MANY_SUPERHEROES,
    HOW_MANY_SUPERHEROES_RESPONSE,
    HOW_MANY_SUPERHEROES_NO_DFID,
)


def test_main_no_args(capsys):
    """Test that main function prints help when no command is given."""
    try:
        main(["-h"])
    except SystemExit as e:
        assert e.code == 0

    captured = capsys.readouterr()
    assert "usage:" in captured.out


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
