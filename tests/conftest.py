import asyncio
import copy
import json
import os
from typing import Optional
from typing import Union

import pytest
from aiohttp_requests import requests
from dotenv import load_dotenv

from . import postman
from stake.client import HttpClient
from stake.client import StakeClient

load_dotenv()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_client():
    return await StakeClient()


@pytest.fixture(scope="session")
async def test_client_fixture_generator():
    client = await StakeClient()
    client.httpClient = RecorderHttpClient()

    yield client

    # send to postman

    await postman.upload_postman_collection(
        client.httpClient.out_collection,
        os.environ["STAKE_POSTMAN_UNITTEST_COLLECTION_ID"],
        os.environ["STAKE_POSTMAN_MOCK_API_KEY_UNITTEST"],
    )


class RecorderHttpClient(HttpClient):
    """Same as the original but it will also record the http calls to record
    fixtures."""

    def __init__(self):
        self.out_collection = postman.PostmanCollection(
            info=postman.PostmanCollectionInfo(
                name="unit-tests", description="Postman unittest collection"
            ),
            item=[],
        )

    async def get(self, url, payload: dict, headers: dict = None) -> dict:

        response = await requests.get(HttpClient.url(url), headers=headers)

        # response.raise_for_status()
        obfuscated_headers = RecorderHttpClient.obfuscate_headers(headers)
        out_json = await response.json()
        obfuscated_response = RecorderHttpClient.obfuscate_response(out_json)
        request = postman.PostmanCollectionRequest(
            name=f"request_{url}",
            description=f"get {url}",
            header=[
                postman.PostmanCollectionRequestHeader(key=key, value=value)
                for key, value in obfuscated_headers.items()
            ],
            method="GET",
            url=postman.PostmanCollectionRequestUrl(raw="{{url}}/" + url),
        )
        obfuscated_response_headers = RecorderHttpClient.obfuscate_headers(
            response.headers
        )
        out_response = postman.PostmanCollectionResponse(
            originalRequest=request,
            name=f"response {url}",
            status="OK",
            code=response.status,
            body=json.dumps(obfuscated_response),
            header=[
                postman.PostmanCollectionRequestHeader(key=key, value=value)
                for key, value in obfuscated_response_headers.items()
            ],
        )
        item = postman.PostmanCollectionItem(
            name=f"GET {url}", request=request, response=[out_response]
        )
        if item.name not in [item_.name for item_ in self.out_collection.item]:
            self.out_collection.item.append(item)

        return out_json

    @staticmethod
    def obfuscate_headers(headers: Optional[dict]) -> dict:
        obfuscated_headers = headers.copy()
        obfuscated_headers["Stake-Session-Token"] = "{{Stake-Session-Token}}"
        obfuscated_headers["x-api-key"] = "{{x-api-key}}"
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
            "orderNo": "{{$randomProductName}}",
            "dwAccountId": "{{$randomUUID}}",
            "tranWhen": "{{$randomDateRecent}}",
            "referenceNumber": "{{$randomBankAccount}}",
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

        request = postman.PostmanCollectionRequest(
            name=f"request_{url}",
            description=f"get {url}",
            header=[
                postman.PostmanCollectionRequestHeader(key=key, value=value)
                for key, value in obfuscated_headers.items()
            ],
            body=postman.PostmanCollectionRequestBody(
                raw=json.dumps(payload, indent=2)
            ),
            method="POST",
            url=postman.PostmanCollectionRequestUrl(raw="{{url}}/" + url),
        )
        obfuscated_response_headers = RecorderHttpClient.obfuscate_headers(
            response.headers
        )
        out_response = postman.PostmanCollectionResponse(
            originalRequest=request,
            name=f"response {url}",
            status="OK",
            code=response.status,
            body=json.dumps(obfuscated_response, indent=2),
            header=[
                postman.PostmanCollectionRequestHeader(key=key, value=value)
                for key, value in obfuscated_response_headers.items()
            ],
        )
        item = postman.PostmanCollectionItem(
            name=f"POST {url}", request=request, response=[out_response]
        )
        if item.name not in [item_.name for item_ in self.out_collection.item]:
            self.out_collection.item.append(item)

        return out_json
