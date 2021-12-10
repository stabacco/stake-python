import asyncio
import json
import os
import uuid
from copy import deepcopy
from typing import Optional

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
    fake_user_id: str = "7c9bbfae-0000-47b7-0000-0e66d868c2cf"
    user_id: Optional[str] = None

    async def get(self, url: str, payload: dict = None, headers: dict = None) -> dict:
        async with aiohttp.ClientSession(
            headers=headers, raise_for_status=True
        ) as session:
            response = await session.get(self.url(url), headers=headers, json=payload)
            result = await response.json()

            ##
            write_data = {
                "url": "{url}"
                + url.replace(
                    str(RecordingHttpClient.user_id), RecordingHttpClient.fake_user_id
                ),
                "body": payload,
                "payload": result,
                "method": "GET",
            }

            RecordingHttpClient.state.append(write_data)

            return result

    async def post(self, url: str, payload: dict, headers: dict = None) -> dict:
        async with aiohttp.ClientSession(
            headers=headers, raise_for_status=True
        ) as session:
            response = await session.post(self.url(url), headers=headers, json=payload)
            result = await response.json()
            write_data = {
                "url": "{url}" + url.replace(str(self.user_id), self.fake_user_id),
                "body": payload,
                "payload": result,
                "method": "POST",
            }

            self.state.append(write_data)

            return result

    async def delete(
        self, url: str, payload: dict = None, headers: dict = None
    ) -> bool:
        async with aiohttp.ClientSession(
            headers=headers, raise_for_status=True
        ) as session:
            response = await session.delete(
                self.url(url), headers=headers, json=payload
            )
            result = await response.json()
            write_data = {
                "url": "{url}" + url,
                "body": payload,
                "payload": result,
                "method": "DELETE",
            }

            self.state.append(write_data)

            return response.status <= 399

    @staticmethod
    def redacted(result, context: dict = None):

        from faker import Faker

        context_str = str(context)

        fake = Faker()
        fake.seed_instance(1234)
        fake_user_id = RecordingHttpClient.fake_user_id
        fake_order_id = uuid.UUID(
            str(uuid.uuid3(uuid.NAMESPACE_URL, context_str)), version=4
        )

        fake_transaction_id = "HHI." + str(fake_order_id)
        obfuscated_fields = {
            "id": str(fake_order_id),
            "firstName": fake.first_name(),
            "lastName": fake.last_name(),
            "phoneNumber": fake.phone_number(),
            "ackSignedWhen": str(fake.date_this_decade()),
            "referralCode": fake.pystr_format(),
            "userId": "7c9bbfae-0000-47b7-0000-0e66d868c2cf",
            "username": fake.simple_profile()["username"],
            "emailAddress": fake.email(),
            "password": fake.password(),
            "dw_id": str(fake_order_id),
            "dw_AccountId": str(fake_order_id),
            "dw_AccountNumber": fake.pystr_format(),
            "macAccountNumber": fake.pystr_format(),
            "finTranID": str(fake_order_id),
            "orderID": fake_transaction_id,
            "orderId": fake_transaction_id,
            "userID": fake_user_id,
            "orderNo": fake.pystr_format(),
            "dwAccountId": str(fake_order_id),
            "dwOrderId": fake_transaction_id,
            "tranWhen": str(fake.date_time_this_decade()),
            "referenceNumber": fake.pystr_format(),
            "productWatchlistID": str(fake_order_id),
            "createdWhen": str(fake.date_time_this_decade()),
        }

        if isinstance(result, list):
            result = [RecordingHttpClient.redacted(res) for res in result]
        elif isinstance(result, dict):
            for k, v in result.items():
                if isinstance(v, dict):
                    result[k] = RecordingHttpClient.redacted(v, context={k: v})
                elif isinstance(v, list):
                    result[k] = [
                        RecordingHttpClient.redacted(res, context={k: v}) for res in v
                    ]
                if k in obfuscated_fields:
                    result[k] = obfuscated_fields[k]

        return result


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
            state = deepcopy(client.http_client.state)
            RecordingHttpClient.user_id = str(client.user.id)
            state = RecordingHttpClient.redacted(state)
            json.dump(
                {function_name: state},
                open(f"tests/fixtures/{function_name}.json", "w"),
                indent=4,
            )


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
