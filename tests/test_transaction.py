from typing import Union

import pytest

import stake
from stake import constant, transaction
from stake.asx import transaction as asx_transaction


@pytest.mark.parametrize(
    "exchange, request_",
    (
        (constant.NYSE, transaction.TransactionRecordRequest(limit=3)),
        (constant.ASX, asx_transaction.TransactionRecordRequest(limit=3)),
    ),
)
@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_list_transactions(
    tracing_client: stake.StakeClient,
    exchange: Union[constant.ASXUrl, constant.NYSEUrl],
    request_: Union[
        asx_transaction.TransactionRecordRequest, transaction.TransactionRecordRequest
    ],
):
    tracing_client.set_exchange(exchange)
    transactions = await tracing_client.transactions.list(request_)

    assert transactions
