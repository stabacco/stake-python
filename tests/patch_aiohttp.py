import attr
from aiohttp import ClientResponse
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
