import json

import pytest
from snowleopard.cli import main

from .conftest import HOW_MANY_SUPERHEROES


def test_main_no_args(capsys):
    """Test that main function prints help when no command is given."""
    try:
        main(["-h"])
    except SystemExit as e:
        assert e.code == 0

    captured = capsys.readouterr()
    assert "usage:" in captured.out


@pytest.mark.vcr(HOW_MANY_SUPERHEROES)
def test_retrieve_command(capsys, loc, superheroes, token, how_many_superheroes_q):
    main(["-l", loc, "-t", "token", "retrieve", superheroes, how_many_superheroes_q])

    captured = capsys.readouterr()
    assert "6895" in captured.out
    assert json.loads(captured.out)
