import os
from pathlib import Path
from urllib.request import Request

import pytest
from snowleopard.client import SnowLeopardClient
from snowleopard.async_client import AsyncSnowLeopardClient


CASSETTES_DIR = Path(__file__).parent / "cassettes"
HOW_MANY_SUPERHEROES = CASSETTES_DIR / "how_many_superheroes.yaml"


@pytest.fixture(scope="module")
def vcr_config(superheroes):
    def replace_subs(request: Request):
        request.uri = request.uri.replace(superheroes, "superheroes_dfid")
        return request

    return {
        "filter_headers": ["authorization"],
        "before_record_request": replace_subs,
    }


@pytest.fixture(scope="module")
def superheroes():
    # when client supports uploading datafiles, this will become part of workflow
    return os.environ.get("SUPERHEROES_DFID", "superheroes_dfid")


@pytest.fixture
def token():
    return os.environ.get("SNOWLEOPARD_API_KEY", "test_token")


@pytest.fixture
def loc():
    return "https://dev.snowleopard.ai/"


@pytest.fixture
def client(token, loc):
    return SnowLeopardClient(loc=loc, token=token)


@pytest.fixture
def async_client(token, loc):
    return AsyncSnowLeopardClient(loc=loc, token=token)


@pytest.fixture
def how_many_superheroes_q():
    return "How many superheroes are there?"
