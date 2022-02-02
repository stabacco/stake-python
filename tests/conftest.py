import asyncio
import json
import uuid

import pytest
from dotenv import load_dotenv
from faker import Faker

from stake.client import StakeClient

load_dotenv()


@pytest.fixture
async def tracing_client(request, mocker):
    async with StakeClient() as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


def redact_sensitive_data(response):

    fake = Faker()
    fake.seed_instance(1234)
    fake_user_id = "7c9bbfae-0000-47b7-0000-0e66d868c2cf"
    fake_order_id = uuid.UUID(str(uuid.uuid3(uuid.NAMESPACE_URL, "test")), version=4)

    fake_transaction_id = "HHI." + str(fake_order_id)
    obfuscated_fields = {
        "id": str(uuid.uuid4()),
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
        "cashAvailableForWithdrawal": 1000,
        "cashAvailableForTrade": 800,
        "dwCashAvailableForWithdrawal": 1000,
        "reference": fake.pystr_format(),
        "comment": fake.pystr_format(),
        "tranAmount": 1000,
    }

    def _redact_response_body(body):
        if not body:
            return body

        if isinstance(body, list):
            body = [_redact_response_body(res) for res in body]
        elif isinstance(body, dict):
            for field, value in body.items():
                if isinstance(value, list):
                    body[field] = [_redact_response_body(res) for res in value]
                elif isinstance(value, dict):
                    body[field] = _redact_response_body(value)
                else:
                    body[field] = obfuscated_fields.get(field, value)

        return body

    body = json.loads(response["body"]["string"])

    response["body"]["string"] = bytes(json.dumps(_redact_response_body(body)), "utf-8")

    response["headers"] = {}
    return response


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": ["stake-session-token"],
        "before_record_response": redact_sensitive_data,
    }
