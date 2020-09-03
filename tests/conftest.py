import asyncio
import copy
import json
import uuid
from typing import Optional, Union

import pytest
from aiohttp import ClientSession, TraceConfig
from attr import asdict
from dotenv import load_dotenv

from stake.client import HttpClient, StakeClient
from tests.patch_aiohttp import SharedRequests

from . import postman

load_dotenv()

from yarl import URL


async def on_request_start(session, trace_config_ctx, params):
    # print("TRACE---CONTEXT", session._current_test_name)
    # print("DDD", asdict(params))
    trace_config_ctx.request_id = str(uuid.uuid4())
    body = None
    # if params.data:
    #     body = params.data._value
    ## POSTMAN
    raw_url = str(params.url.raw_path)

    headers = params.headers
    request = postman.PostmanCollectionRequest(
        name=f"request_{trace_config_ctx.request_id}",
        description=f"H {params.method} {trace_config_ctx.request_id} {raw_url}",
        header=[
            postman.PostmanCollectionRequestHeader(key=key, value=value)
            for key, value in headers.items()
        ],
        method=str(params.method),
        url=postman.PostmanCollectionRequestUrl(raw=raw_url, host=[params.url.host]),
        body=postman.PostmanCollectionRequestBody(raw=body) if body else None,
    )
    trace_config_ctx.request = request
    # POSTMAN

    # session.info[trace_config_ctx.request_id]['request'] = asdict(params)
    print("Starting request", trace_config_ctx, params)


async def on_request_end(session, trace_config_ctx, params):
    # print("TRACE++++CONTEXT", session._current_test_name)
    print(trace_config_ctx.request_id)
    response_body = await params.response.json()

    # obfuscated_response_headers = RecorderHttpClient.obfuscate_headers(
    #     response.headers
    # )

    raw_url = str(params.url.raw_path)
    original_request = params.response.request_info
    original_request_url = original_request.url.raw_path
    request = postman.PostmanCollectionRequest(
        name=f"R request_{trace_config_ctx.request_id}",
        description=f"R {params.method} {trace_config_ctx.request_id} {raw_url}",
        header=[
            postman.PostmanCollectionRequestHeader(key=key, value=value)
            for key, value in original_request.headers.items()
        ],
        method=str(params.method),
        url=postman.PostmanCollectionRequestUrl(
            raw=raw_url, host=[original_request.url.host]
        ),
    )

    out_response = postman.PostmanCollectionResponse(
        originalRequest=request,
        name=f"response_{trace_config_ctx.request_id}",
        status="OK",
        code=params.response.status,
        body=json.dumps(response_body),
        header=[
            postman.PostmanCollectionRequestHeader(key=key, value=value)
            for key, value in params.headers.items()
        ],
    )
    item = postman.PostmanCollectionItem(
        name=f"{params.method} {raw_url}",
        request=trace_config_ctx.request,
        response=[out_response],
    )

    session.current_collection_item.item.append(item)

    print("Ending request", trace_config_ctx, (asdict(params)))


trace_config = TraceConfig()
trace_config.on_request_start.append(on_request_start)
trace_config.on_request_end.append(on_request_end)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def patch_aiohttp(session_mocker):
    from .patch_aiohttp import TraceRequestEndParams, TraceRequestStartParams

    session_mocker.patch(
        "aiohttp.tracing.TraceRequestStartParams", new=TraceRequestStartParams
    )
    session_mocker.patch(
        "aiohttp.tracing.TraceRequestEndParams", new=TraceRequestEndParams
    )


@pytest.fixture(scope="session")
async def patch_client_session_response(session_mocker, patch_aiohttp):
    from .patch_aiohttp import ClientRequest, ClientResponse

    recording_session = ClientSession(
        # trace_configs=[trace_config],
        request_class=ClientRequest,
        response_class=ClientResponse,
    )
    recording_session.collection = postman.PostmanCollection(
        info=postman.PostmanCollectionInfo(
            name="unit-tests", description="Postman example collection"
        ),
        item=[],
    )

    recording_session.current_collection_item = recording_session.collection
    session_mocker.patch.object(HttpClient, "_session", recording_session)


@pytest.fixture(scope="session")
async def session_tracing_client(patch_client_session_response):

    client = StakeClient()
    await client.login(client._login_request)
    yield client

    collection = client.httpClient._session.collection
    data = {"collection": collection.dict(by_alias=True)}
    with open("collection.json", "w") as f:
        json.dump(data, f, indent=2)

    # pprint.pprint(SharedRequests._shared_state)
    # for uid, data in SharedRequests._shared_state.items():
    #     print(uid)
    #     print(await data["request"].as_postman_request(uid))
    #     print(await data["response"].as_postman_response(data['request'], uid))
    import os
    import pprint

    await postman.upload_postman_collection(
        collection,
        os.environ["STAKE_POSTMAN_UNITTEST_COLLECTION_ID"],
        os.environ["STAKE_POSTMAN_MOCK_API_KEY_UNITTEST"],
    )


@pytest.fixture(scope="function")
async def tracing_client(request, session_tracing_client):
    test_name = f"{request.module.__name__}.{request.node.name}"
    item = postman.PostmanCollectionItem(name=test_name, item=[])
    session_tracing_client.httpClient._session.collection.item.append(item)
    session_tracing_client.httpClient._session.current_collection_item = item
    yield session_tracing_client


@pytest.fixture(scope="function")
async def test_client_fixture_generator(patch_client_session_response, current_folder):
    client = await StakeClient()
    client.httpClient = RecorderHttpClient()

    yield client

    # send to postman

    # await postman.upload_postman_collection(
    #     client.httpClient.out_collection,
    #     os.environ["STAKE_POSTMAN_UNITTEST_COLLECTION_ID"],
    #     os.environ["STAKE_POSTMAN_MOCK_API_KEY_UNITTEST"],
    # )


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

        response = await super.get(*args, **kwargs)

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
            "password": "{{$randomPassword}}",
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
