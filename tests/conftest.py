import asyncio
import json
import sys
import uuid

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from faker import Faker

from stake.client import StakeClient

load_dotenv()


@pytest_asyncio.fixture
async def tracing_client(request, mocker):
    async with StakeClient() as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    if sys.version_info < (3, 10):
        loop = asyncio.get_event_loop()
    else:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()

        asyncio.set_event_loop(loop)
    yield loop
    loop.close()


def redact_sensitive_data(response):

    if not response["body"].get("string", None):
        response["headers"] = {}
        return response

    fake = Faker()
    fake.seed_instance(1234)
    fake_user_id = "7c9bbfae-0000-47b7-0000-0e66d868c2cf"
    fake_order_id = uuid.UUID(str(uuid.uuid3(uuid.NAMESPACE_URL, "test")), version=4)

    fake_transaction_id = f"HHI.{str(fake_order_id)}"
    obfuscated_fields = {
        "ackSignedWhen": str(fake.date_this_decade()),
        "brokerOrderId": 11111,
        "buyingPower": 1000.0,
        "cashAvailableForExpressWithdrawal": 1000,
        "cashAvailableForTrade": 800,
        "cashAvailableForWithdrawal": 1000,
        "cashAvailableForWithdrawalRaw": 1000,
        "cashAvailableForTransfer": 1000,
        "cashBalance": 1000.0,
        "comment": fake.pystr_format(),
        "createdWhen": str(fake.date_time_this_decade()),
        "dw_AccountId": str(fake_order_id),
        "dw_AccountNumber": fake.pystr_format(),
        "dw_id": str(fake_order_id),
        "dwAccountId": str(fake_order_id),
        "dwCashAvailableForWithdrawal": 1000,
        "dwOrderId": fake_transaction_id,
        "emailAddress": fake.email(),
        "finTranID": str(fake_order_id),
        "firstName": fake.first_name(),
        "id": str(fake_order_id),
        "lastName": fake.last_name(),
        "liquidCash": 1000.0,
        "macAccountNumber": fake.pystr_format(),
        "openQty": 100,
        "orderID": fake_transaction_id,
        "orderId": fake_transaction_id,
        "orderNo": fake.pystr_format(),
        "password": fake.password(),
        "phoneNumber": fake.phone_number(),
        "postedBalance": 4000,
        "productWatchlistID": str(fake_order_id),
        "reference": fake.pystr_format(),
        "referenceNumber": fake.pystr_format(),
        "referralCode": fake.pystr_format(),
        "settledCash": 10000.00,
        "tranAmount": 1000,
        "tranWhen": str(fake.date_time_this_decade()),
        "unrealizedDayPLPercent": 1.0,
        "unrealizedPL": 1.0,
        "userId": "7c9bbfae-0000-47b7-0000-0e66d868c2cf",
        "userID": fake_user_id,
        "username": fake.simple_profile()["username"],
        "watchlistId": str(fake_order_id),
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
