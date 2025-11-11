import os
from pathlib import Path
from urllib.request import Request

import pytest

CASSETTES_DIR = Path(__file__).parent / "cassettes"

HOW_MANY_SUPERHEROES = CASSETTES_DIR / "how_many_superheroes.yaml"


@pytest.fixture(scope="module")
def dfid():
    # when client supports uploading datafiles, this will become part of workflow
    return os.environ.get("SNOWLEOPARD_PY_TEST_DFID", "test_dfid")


@pytest.fixture(scope='module')
def vcr_config(dfid):
    def replace_dfid(request: Request):
        request.uri = request.uri.replace(dfid, "test_dfid")
        return request

    return {
        "filter_headers": ["authorization"],
        "before_record_request": replace_dfid,
    }
