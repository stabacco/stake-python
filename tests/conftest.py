import asyncio
import json
import os
from copy import deepcopy

import aiohttp
import pkg_resources
import pytest
from aioresponses import aioresponses
from dotenv import load_dotenv

from stake.client import HttpClient, StakeClient
from stake.constant import STAKE_URL

load_dotenv()


class RecordingHttpClient(HttpClient):

    state: list = []

    @staticmethod
    async def get(url: str, payload: dict = None, headers: dict = None) -> dict:
        async with aiohttp.ClientSession(
            headers=headers, raise_for_status=True
        ) as session:
            response = await session.get(
                RecordingHttpClient.url(url), headers=headers, json=payload
            )
            result = await response.json()

            ##
            write_data = {
                "url": "{url}" + url,
                "body": payload,
                "payload": result,
                "method": "GET",
            }

            RecordingHttpClient.state.append(RecordingHttpClient.redacted(write_data))

            return result

    @staticmethod
    async def post(url: str, payload: dict, headers: dict = None) -> dict:
        async with aiohttp.ClientSession(
            headers=headers, raise_for_status=True
        ) as session:
            response = await session.post(
                RecordingHttpClient.url(url), headers=headers, json=payload
            )
            result = await response.json()
            write_data = {
                "url": "{url}" + url,
                "body": payload,
                "payload": result,
                "method": "POST",
            }

            RecordingHttpClient.state.append(RecordingHttpClient.redacted(write_data))

            return result

    @staticmethod
    def redacted(result):
        return result
        out = deepcopy(result)
        from faker import Faker

        fake = Faker()
        fake.seed_instance(1234)

        payload = result["payload"]
        if not payload:
            return result

        obfuscated_fields = {
            "firstName": fake.first_name(),
            "lastName": fake.last_name(),
            "phoneNumber": fake.phone_number(),
            "ackSignedWhen": str(fake.date_this_decade()),
            "referralCode": fake.pystr_format(),
            "userId": fake.uuid4(),
            "username": fake.simple_profile()["username"],
            "emailAddress": fake.email(),
            "password": fake.password(),
            "dw_id": fake.uuid4(),
            "dw_AccountId": fake.uuid4(),
            "dw_AccountNumber": fake.pystr_format(),
            "macAccountNumber": fake.pystr_format(),
            "finTranID": fake.uuid4(),
            "orderID": fake.uuid4(),
            "orderNo": fake.pystr_format(),
            "dwAccountId": fake.uuid4(),
            "tranWhen": str(fake.date_this_decade()),
            "referenceNumber": fake.pystr_format(),
        }

        if isinstance(payload, list):
            for load in payload:
                for field in load:
                    if field in obfuscated_fields:
                        load[field] = obfuscated_fields[field]
        else:
            for field in payload:
                if field in obfuscated_fields:
                    payload[field] = obfuscated_fields[field]
        print("PPPPP", payload)
        out["payload"] = payload
        return out


@pytest.fixture
async def tracing_client(request, mocker):
    mocker.patch("stake.client.HttpClient", new=RecordingHttpClient)
    RecordingHttpClient.state = []
    function_name = f"{request.node.module.__name__}.{request.node.name}"
    filename = pkg_resources.resource_filename(
        __name__, f"fixtures/{function_name}.json"
    )
    if os.path.exists(filename):
        fixtures = json.load(open(filename))
        with aioresponses() as m:
            mock_datas = fixtures[function_name]
            assert mock_datas
            for mock_data in mock_datas:
                m.add(
                    mock_data["url"].format(url=STAKE_URL),
                    method=mock_data.get("method"),
                    body=mock_data["body"],
                    payload=mock_data["payload"],
                )
            async with StakeClient() as client:
                yield client

    else:
        async with StakeClient() as client:
            yield client
            json.dump(
                {function_name: client.httpClient.state},
                open(f"tests/fixtures/{function_name}.json", "w"),
                indent=4,
            )


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


# @pytest.fixture(scope="session")
# async def tracing_client():

#     client = StakeClient()
#     await client.login(client._login_request)
#     yield client

#
# @pytest.fixture(scope="session")
# def patch_aiohttp(session_mocker):
#     from .patch_aiohttp import TraceRequestEndParams, TraceRequestStartParams
#
#     session_mocker.patch(
#         "aiohttp.tracing.TraceRequestStartParams", new=TraceRequestStartParams
#     )
#     session_mocker.patch(
#         "aiohttp.tracing.TraceRequestEndParams", new=TraceRequestEndParams
#     )
#
#
# @pytest.fixture(scope="session")
# async def patch_client_session_response(session_mocker, patch_aiohttp):
#     from .patch_aiohttp import ClientRequest, ClientResponse
#
#     recording_session = ClientSession(
#         # trace_configs=[trace_config],
#         request_class=ClientRequest,
#         response_class=ClientResponse,
#     )
#     recording_session.collection = postman.PostmanCollection(
#         info=postman.PostmanCollectionInfo(
#             name="unit-tests", description="Postman example collection"
#         ),
#         item=[],
#     )
#
#     recording_session.current_collection_item = recording_session.collection
#     session_mocker.patch.object(HttpClient, "_session", recording_session)
#
#
# @pytest.fixture(scope="session")
# async def session_tracing_client(patch_client_session_response):
#
#     client = StakeClient()
#     await client.login(client._login_request)
#     yield client
#
#     collection = client.httpClient._session.collection
#     data = {"collection": collection.dict(by_alias=True)}
#     with open("collection.json", "w") as f:
#         json.dump(data, f, indent=2)
#
#     # pprint.pprint(SharedRequests._shared_state)
#     # for uid, data in SharedRequests._shared_state.items():
#     #     print(uid)
#     #     print(await data["request"].as_postman_request(uid))
#     #     print(await data["response"].as_postman_response(data['request'], uid))
#     import os
#     import pprint
#
#     await postman.upload_postman_collection(
#         collection,
#         os.environ["STAKE_POSTMAN_UNITTEST_COLLECTION_ID"],
#         os.environ["STAKE_POSTMAN_MOCK_API_KEY_UNITTEST"],
#     )
#
#
# @pytest.fixture(scope="function")
# async def tracing_client_old(request, session_tracing_client):
#     test_name = f"{request.module.__name__}.{request.node.name}"
#     item = postman.PostmanCollectionItem(name=test_name, item=[])
#     session_tracing_client.httpClient._session.collection.item.append(item)
#     session_tracing_client.httpClient._session.current_collection_item = item
#     yield session_tracing_client
#
#
# @pytest.fixture(scope="function")
# async def test_client_fixture_generator(patch_client_session_response, current_folder):
#     client = await StakeClient()
#     client.httpClient = RecorderHttpClient()
#
#     yield client
#
#     # send to postman
#
#     # await postman.upload_postman_collection(
#     #     client.httpClient.out_collection,
#     #     os.environ["STAKE_POSTMAN_UNITTEST_COLLECTION_ID"],
#     #     os.environ["STAKE_POSTMAN_MOCK_API_KEY_UNITTEST"],
#     # )
#
#
# class RecorderHttpClient(HttpClient):
#     """Same as the original but it will also record the http calls to record
#     fixtures."""
#
#     def __init__(self):
#         self.out_collection = postman.PostmanCollection(
#             info=postman.PostmanCollectionInfo(
#                 name="unit-tests", description="Postman unittest collection"
#             ),
#             item=[],
#         )
#
#     async def get(self, url, payload: dict, headers: dict = None) -> dict:
#
#         response = await super.get(*args, **kwargs)
#
#         # response.raise_for_status()
#         obfuscated_headers = RecorderHttpClient.obfuscate_headers(headers)
#         out_json = await response.json()
#         obfuscated_response = RecorderHttpClient.obfuscate_response(out_json)
#         request = postman.PostmanCollectionRequest(
#             name=f"request_{url}",
#             description=f"get {url}",
#             header=[
#                 postman.PostmanCollectionRequestHeader(key=key, value=value)
#                 for key, value in obfuscated_headers.items()
#             ],
#             method="GET",
#             url=postman.PostmanCollectionRequestUrl(raw="{{url}}/" + url),
#         )
#         obfuscated_response_headers = RecorderHttpClient.obfuscate_headers(
#             response.headers
#         )
#         out_response = postman.PostmanCollectionResponse(
#             originalRequest=request,
#             name=f"response {url}",
#             status="OK",
#             code=response.status,
#             body=json.dumps(obfuscated_response),
#             header=[
#                 postman.PostmanCollectionRequestHeader(key=key, value=value)
#                 for key, value in obfuscated_response_headers.items()
#             ],
#         )
#         item = postman.PostmanCollectionItem(
#             name=f"GET {url}", request=request, response=[out_response]
#         )
#         if item.name not in [item_.name for item_ in self.out_collection.item]:
#             self.out_collection.item.append(item)
#
#         return out_json
#
#     @staticmethod
#     def obfuscate_headers(headers: Optional[dict]) -> dict:
#         obfuscated_headers = headers.copy()
#         obfuscated_headers["Stake-Session-Token"] = "{{Stake-Session-Token}}"
#         obfuscated_headers["x-api-key"] = "{{x-api-key}}"
#         return obfuscated_headers
#
#     @staticmethod
#     def obfuscate_response(response: Union[dict, list]) -> Union[dict, list]:
#         obfuscated_fields = {
#             "firstName": "{{$randomFirstName}}",
#             "lastName": "{{$randomLastName}}",
#             "phoneNumber": "{{$randomPhoneNumber}}",
#             "ackSignedWhen": "{{$randomDateRecent}}",
#             "referralCode": "{{$randomUserName}}",
#             "userId": "{{$randomUUID}}",
#             "username": "{{$randomUserName}}",
#             "emailAddress": "{{$randomEmail}}",
#             "password": "{{$randomPassword}}",
#             "dw_id": "{{$randomUUID}}",
#             "dw_AccountId": "{{$randomUUID}}",
#             "dw_AccountNumber": "{{$randomBankAccountName}}",
#             "macAccountNumber": "{{$randomBankAccountIban}}",
#             "finTranID": "{{$randomUUID}}",
#             "orderID": "{{$randomUUID}}",
#             "orderNo": "{{$randomProductName}}",
#             "dwAccountId": "{{$randomUUID}}",
#             "tranWhen": "{{$randomDateRecent}}",
#             "referenceNumber": "{{$randomBankAccount}}",
#         }
#         obfuscated_responses = copy.deepcopy(response)
#         is_dict = isinstance(obfuscated_responses, dict)
#         if is_dict:
#             obfuscated_responses = [obfuscated_responses]
#
#         for obfuscated_response in obfuscated_responses:
#             for field, field_value in obfuscated_fields.items():
#                 if field in obfuscated_response:
#                     obfuscated_response[field] = field_value
#
#         if is_dict:
#             return obfuscated_responses[0]
#
#         return obfuscated_responses
#
#     async def post(self, url, payload: dict, headers: dict = None) -> dict:
#         response = await requests.post(
#             HttpClient.url(url), headers=headers, json=payload
#         )
#         # return await response.json()
#         obfuscated_headers = RecorderHttpClient.obfuscate_headers(headers)
#         out_json = await response.json()
#         obfuscated_response = RecorderHttpClient.obfuscate_response(out_json)
#
#         request = postman.PostmanCollectionRequest(
#             name=f"request_{url}",
#             description=f"get {url}",
#             header=[
#                 postman.PostmanCollectionRequestHeader(key=key, value=value)
#                 for key, value in obfuscated_headers.items()
#             ],
#             body=postman.PostmanCollectionRequestBody(
#                 raw=json.dumps(payload, indent=2)
#             ),
#             method="POST",
#             url=postman.PostmanCollectionRequestUrl(raw="{{url}}/" + url),
#         )
#         obfuscated_response_headers = RecorderHttpClient.obfuscate_headers(
#             response.headers
#         )
#         out_response = postman.PostmanCollectionResponse(
#             originalRequest=request,
#             name=f"response {url}",
#             status="OK",
#             code=response.status,
#             body=json.dumps(obfuscated_response, indent=2),
#             header=[
#                 postman.PostmanCollectionRequestHeader(key=key, value=value)
#                 for key, value in obfuscated_response_headers.items()
#             ],
#         )
#         item = postman.PostmanCollectionItem(
#             name=f"POST {url}", request=request, response=[out_response]
#         )
#         if item.name not in [item_.name for item_ in self.out_collection.item]:
#             self.out_collection.item.append(item)
#
#         return out_json
