import os
from pathlib import Path
from typing import Union
from urllib.request import Request

import pytest
from dotenv import load_dotenv
from snowleopard.async_client import AsyncSnowLeopardClient
from snowleopard.client import SnowLeopardClient

load_dotenv()

CASSETTES_DIR = Path(__file__).parent / "cassettes"
HOW_MANY_SUPERHEROES = str(CASSETTES_DIR / "how_many_superheroes.yaml")
HOW_MANY_SUPERHEROES_RESPONSE = str(
    CASSETTES_DIR / "how_many_superheroes_response.yaml"
)


@pytest.fixture(scope="module")
def vcr_config(superheroes, loc):
    def replace_subs(request: Request):
        request.uri = request.uri.replace(superheroes, "superheroes_dfid")
        request.uri = request.uri.replace(loc.rstrip("/"), "https://api.snowleopard.ai")
        return request

    return {
        "filter_headers": ["authorization"],
        "before_record_request": replace_subs,
        "record_mode": os.environ.get("SNOWLEOPARD_TEST_RECORD_MODE", "none"),
    }


@pytest.fixture(scope="module")
def superheroes():
    # when client supports uploading datafiles, this will become part of workflow
    return os.environ.get("SUPERHEROES_DFID", "superheroes_dfid")


@pytest.fixture
def token():
    return os.environ.get("SNOWLEOPARD_API_KEY", "test_token")


@pytest.fixture(scope="module")
def loc():
    return os.environ.get("SNOWLEOPARD_LOC", "https://api.snowleopard.ai/")


@pytest.fixture
def client(token, loc):
    return SnowLeopardClient(loc=loc, token=token)


@pytest.fixture
def async_client(token, loc):
    return AsyncSnowLeopardClient(loc=loc, token=token)


@pytest.fixture(params=["client", "async_client"])
def any_client(request) -> Union[SnowLeopardClient, AsyncSnowLeopardClient]:
    return request.getfixturevalue(request.param)


@pytest.fixture
def how_many_superheroes_q():
    return "How many superheroes are there?"
