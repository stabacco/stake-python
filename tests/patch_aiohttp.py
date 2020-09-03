import attr
from aiohttp import ClientResponse
from aiohttp.client_reqrep import ClientRequest as BaseClientRequest
from aiohttp.client_reqrep import ClientResponse as BaseClientResponse
from aiohttp.payload import JsonPayload
from multidict import CIMultiDict
from pydantic import BaseModel, fields
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
            "request": self,
            "response": response,
        }
        response._uid = uid
        response._request = self
        return response

    async def as_postman_request(self, uid):
        from . import postman

        # raise RuntimeError(self.body, bool(self.body))
        body = None
        if self.body != (b"",):
            body = postman.PostmanCollectionRequestBody(
                raw=self.body._value if self.body else ""
            )

        return postman.PostmanCollectionRequest(
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
            body=body,
        )


class ClientResponse(BaseClientResponse):
    async def as_postman_response(self):
        from . import postman

        req = await self._request.as_postman_request(self._uid)
        # req = req.dict(by_alias=True)
        response = postman.PostmanCollectionResponse(
            originalRequest=req,
            name=f"response_{self._uid}",
            url=postman.PostmanCollectionRequestUrl(
                raw=str(self.url.raw_path), host=[self.host]
            ),
            status="OK",  # TODO
            code=self.status,
            body=await self.text(),
            header=[
                postman.PostmanCollectionRequestHeader(key=key, value=value)
                for key, value in self.headers.items()
            ],
        )
        item = postman.PostmanCollectionItem(
            name=f"{self.method} {self.url.raw_path}", request=req, response=[response],
        )
        print("Appending item", item)
        self._session.current_collection_item.item.append(item)

        return response

    async def json(self):
        result = await super().json()
        await self.as_postman_response()
        return result

    # def release(self):
    #     raise RuntimeError("this called")
    #     result = super().release()
    #     self.as_postman_response()
    #     return result
