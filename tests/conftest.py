import asyncio
import copy
from typing import List
from typing import Optional
from typing import Union

import pytest
from aiohttp_requests import requests
from pydantic import BaseModel

from stake.client import HttpClient
from stake.client import StakeClient


class PostmanCollectionInfo(BaseModel):
    _postman_id: str = "f175f235-0eb7-4e9b-b6ee-57de3865612b"
    name: str
    description: str = "Stake api collection"
    schema_: str = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"


class PostmanCollectionRequestHeader(BaseModel):
    key: str
    value: str
    type: str = "text"


class PostmanCollectionRequestUrl(BaseModel):
    raw: str
    host: str = "{{url}}"

    @property
    def path(self) -> list:
        return self.raw.replace(self.host, "").split("/")


class PostmanCollectionRequestBody(BaseModel):

    mode: str = "raw"
    raw: str  # json-encoded


class PostmanCollectionRequest(BaseModel):
    name: str
    method: str
    header: List[PostmanCollectionRequestHeader]
    url: PostmanCollectionRequestUrl
    description: str
    body: Optional[PostmanCollectionRequestBody]


class PostmanCollectionResponse(BaseModel):
    name: str
    originalRequest: PostmanCollectionRequest
    status: str
    code: int
    _postman_previewlanguage: str = "json"
    header: List[PostmanCollectionRequestHeader]
    cookie: list = []
    body: str  # json-encoded.
    variable: list = []  # no variables atm
    protocolProfileBehavior: dict = {}


class PostmanCollectionItem(BaseModel):
    name: str
    request: PostmanCollectionRequest
    response: PostmanCollectionResponse


class PostmanCollection(BaseModel):
    info: PostmanCollectionInfo
    item: List[PostmanCollectionItem]


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_client():
    client = await StakeClient()
    return client


@pytest.fixture(scope="session")
async def test_client_fixture_generator():
    client = await StakeClient()
    client.httpClient = RecorderHttpClient()

    with open("./stake-fixtures.json", "w") as f:
        yield client
        f.write(client.out_collection)
    f.close()


class RecorderHttpClient(HttpClient):
    """Same as the original but it will also record the http calls to record
    fixtures."""

    def __init__(self):
        self.out_collection = PostmanCollection(
            info=PostmanCollectionInfo(
                name="unittests", description="Postman unittest collection"
            ),
            item=[],
        )

    async def get(self, url: str, headers: dict = None) -> dict:
        import json

        response = await requests.get(HttpClient.url(url), headers=headers)

        # response.raise_for_status()
        obfuscated_headers = RecorderHttpClient.obfuscate_headers(headers)
        out_json = await response.json()
        obfuscated_response = RecorderHttpClient.obfuscate_response(out_json)
        request = PostmanCollectionRequest(
            name=f"request_{url}",
            description=f"get {url}",
            header=[
                PostmanCollectionRequestHeader(key=key, value=value)
                for key, value in obfuscated_headers.items()
            ],
            method="GET",
            url=PostmanCollectionRequestUrl(raw=url),
        )
        obfuscated_response_headers = RecorderHttpClient.obfuscate_headers(
            response.headers
        )
        out_response = PostmanCollectionResponse(
            originalRequest=request,
            name=f"response {url}",
            status="OK",
            code=response.status,
            body=json.dumps(obfuscated_response),
            header=[
                PostmanCollectionRequestHeader(key=key, value=value)
                for key, value in obfuscated_response_headers.items()
            ],
        )
        item = PostmanCollectionItem(
            name=f"GET {url}", request=request, response=out_response
        )
        if item.name not in [item_.name for item_ in self.out_collection.item]:
            print(f"APPeNDING ITEM FROM {item.name}:")
            self.out_collection.item.append(item)

        return out_json

    @staticmethod
    def obfuscate_headers(headers: Optional[dict]) -> dict:
        obfuscated_headers = headers.copy()
        obfuscated_headers["Stake-Session-Token"] = "{{$randomUUID}}"
        return obfuscated_headers

    @staticmethod
    def obfuscate_response(response: Union[dict, list]) -> Union[dict, list]:
        obfuscated_fields = {
            "firstName": "{{$randomFirstName}}",
            "lastName": "{{$randomLastName}}",
            "phoneNumber": "{{$randomPhoneNumber}}",
            "ackSignedWhen": "{{$randomDateRecent}}",
            "referralCode": "{{$randomUserName}}",
            "userId": "{{$randomUUID}}",
            "username": "{{$randomUserName}}",
            "emailAddress": "{{$randomEmail}}",
            "dw_id": "{{$randomUUID}}",
            "dw_AccountId": "{{$randomUUID}}",
            "dw_AccountNumber": "{{$randomBankAccountName}}",
            "macAccountNumber": "{{$randomBankAccountIban}}",
            "finTranID": "{{$randomUUID}}",
            "orderID": "{{$randomUUID}}",
            "orderNo": "{{randomProductName}}",
            "dwAccountId": "{{$randomUUID}}",
            "tranWhen": "{{$randomDateRecent}}",
        }
        obfuscated_responses = copy.deepcopy(response)
        is_dict = isinstance(obfuscated_responses, dict)
        if is_dict:
            obfuscated_responses = [obfuscated_responses]
        for obfuscated_response in obfuscated_responses:
            for field, field_value in obfuscated_fields.items():
                if field in obfuscated_response:
                    obfuscated_response[field] = field_value

        if is_dict:
            return obfuscated_responses[0]

        return obfuscated_responses

    async def post(self, url, payload: dict, headers: dict = None) -> dict:
        response = await requests.post(
            HttpClient.url(url), headers=headers, json=payload
        )
        # return await response.json()
        obfuscated_headers = RecorderHttpClient.obfuscate_headers(headers)
        out_json = await response.json()
        obfuscated_response = RecorderHttpClient.obfuscate_response(out_json)
        import json

        request = PostmanCollectionRequest(
            name=f"request_{url}",
            description=f"get {url}",
            header=[
                PostmanCollectionRequestHeader(key=key, value=value)
                for key, value in obfuscated_headers.items()
            ],
            body=PostmanCollectionRequestBody(raw=json.dumps(payload)),
            method="POST",
            url=PostmanCollectionRequestUrl(raw=url),
        )
        obfuscated_response_headers = RecorderHttpClient.obfuscate_headers(
            response.headers
        )
        out_response = PostmanCollectionResponse(
            originalRequest=request,
            name=f"response {url}",
            status="OK",
            code=response.status,
            body=json.dumps(obfuscated_response),
            header=[
                PostmanCollectionRequestHeader(key=key, value=value)
                for key, value in obfuscated_response_headers.items()
            ],
        )
        item = PostmanCollectionItem(
            name=f"POST {url}", request=request, response=out_response
        )
        if item.name not in [item_.name for item_ in self.out_collection.item]:
            print(f"APPeNDING ITEM FROM {item.name}.")
            self.out_collection.item.append(item)

        return out_json
