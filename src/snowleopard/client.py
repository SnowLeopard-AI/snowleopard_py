import os
from typing import Optional

import httpx
from snowleopard.models import RetrieveResponse, SchemaData, ResponseStatus


class SnowLeopardClient:
    client: httpx.Client

    def __init__(self, loc: str = "https://api.snowleopard.ai", token: Optional[str] = None):
        if not loc:
            raise ValueError('Missing required argument "loc"')
        token = token or os.environ.get("SNOWLEOPARD_API_KEY")
        if token is None:
            raise ValueError('Missing required argument "token" and envar "SNOWLEOPARD_API_KEY" not set')

        self.client = httpx.Client(
            base_url=loc,
            headers={"Authorization": f"Bearer {token}"} if token else {},
            timeout=httpx.Timeout(connect=5.0, read=600.0, write=10.0, pool=5.0)
        )


    def retrieve(self, datafile_id: str, user_query: str) -> RetrieveResponse:
        resp = self.client.post(
            # url=f"/datafiles/{datafile_id}/retrieve",
            url=f"api/self/datafiles/{datafile_id}/proxy/retrieve",
            json={"userQuery": user_query}
        )
        resp.raise_for_status()
        resp_json = resp.json()
        return RetrieveResponse(
            callId=resp_json['callId'],
            data = [SchemaData(
                schemaId=d["schemaId"],
                schemaType=d["schemaType"],
                query=d["query"],
                rows=d["rows"],
                querySummary=d["querySummary"],
                rowMax=d["rowMax"],
                isTrimmed=d["isTrimmed"]
            ) for d in resp_json['data']],
            responseStatus=ResponseStatus(resp_json['responseStatus']),
        )
