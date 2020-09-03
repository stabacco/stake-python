import attr
from aiohttp import ClientResponse
from aiohttp.client_reqrep import ClientRequest as BaseClientRequest
from aiohttp.payload import JsonPayload
from multidict import CIMultiDict
from pydantic import BaseModel
from pydantic import fields
from yarl import URL


@attr.s(frozen=True, slots=True)
class TraceRequestStartParams:
    """Parameters sent by the `on_request_start` signal."""

    method = attr.ib(type=str)
    url = attr.ib(type=URL)
    headers = attr.ib(type="CIMultiDict[str]")
    # data= attr.ib(type=dict)


@attr.s(frozen=True, slots=True)
class TraceRequestEndParams:
    """Parameters sent by the `on_request_end` signal."""

    method = attr.ib(type=str)
    url = attr.ib(type=URL)
    headers = attr.ib(type="CIMultiDict[str]")
    response = attr.ib(type=ClientResponse)
    # data = attr.ib(type=dict)


class SharedRequests:
    _shared_state = {}


class ClientRequest(BaseClientRequest):
    async def send(self, conn: "Connection") -> "ClientResponse":
        import uuid

        uid = uuid.uuid4()
        response = await super().send(conn)
        SharedRequests._shared_state[str(uid)] = {
            "request": self.as_postman_request(uid),
            "response": response,
        }
        return response

    def as_postman_request(self, uid):
        from . import postman

        print("ttttt", type(self.body), bool(self.body), self.body)
        postman.PostmanCollectionRequest(
            name=f"request_{uid}",
            description=f"H {self.method} {uid}",
            header=[
                postman.PostmanCollectionRequestHeader(key=key, value=value)
                for key, value in self.headers.items()
            ],
            method=str(self.method),
            url=postman.PostmanCollectionRequestUrl(
                raw=str(self.url.raw_path), host=[self.host]
            ),
            body=postman.PostmanCollectionRequestBody(
                raw=self.body._value if self.body else ""
            ),
        )
