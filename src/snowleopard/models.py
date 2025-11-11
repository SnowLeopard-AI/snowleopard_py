from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Optional


@dataclass
class RetrieveResponse:
    callId: str
    data: list[SchemaData]
    responseStatus: ResponseStatus


@dataclass
class SchemaData:
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
