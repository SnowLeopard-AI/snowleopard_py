from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Optional


@dataclass
class RetrieveResponse:
    responseObjType = "retrieveResponse"

    callId: str
    data: list[SchemaData]
    responseStatus: ResponseStatus


@dataclass
class RetrieveResponseError:
    responseObjType = "apiError"

    callId: str
    responseStatus: str
    description: str


@dataclass
class SchemaData:
    responseObjType = "schemaData"

    schemaId: str
    schemaType: str
    query: str
    rows: list[dict[str, Any]]
    querySummary: dict[str, Any]
    rowMax: Optional[int]
    isTrimmed: bool


class ResponseStatus(StrEnum):
    SUCCESS = "SUCCESS"
    NOT_FOUND_IN_SCHEMA = "NOT_FOUND_IN_SCHEMA"
    UNKNOWN = "UNKNOWN"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    LLM_ERROR = "LLM_ERROR"
    LLM_TOKEN_LIMIT_REACHED = "LLM_TOKEN_LIMIT_REACHED"


_PARSE_OBJS = {
    o.responseObjType: o for o in (RetrieveResponse, RetrieveResponseError, SchemaData)
}


def parse(obj):
    if isinstance(obj, dict):
        kind = _PARSE_OBJS.get(obj.get("__type__"))
        return (
            kind(**{k: parse(v) for k, v in obj.items() if k != "__type__"})
            if kind
            else obj
        )
    elif isinstance(obj, list):
        return [parse(v) for v in obj]
    else:
        return obj
