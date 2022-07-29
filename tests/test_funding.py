from typing import Union

import pytest

import stake
from stake import constant
from stake.asx.funding import FundingRequest as ASXFundingRequest
from stake.funding import TransactionRecordRequest as NYSEFundingRequest


@pytest.mark.parametrize(
    "exchange, request_",
    (
        (constant.NYSE, NYSEFundingRequest(limit=1000)),
        (constant.ASX, ASXFundingRequest(limit=3)),
    ),
)
@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_list_fundings(
    tracing_client: stake.StakeClient,
    exchange: Union[constant.ASXUrl, constant.NYSEUrl],
    request_: Union[ASXFundingRequest, NYSEFundingRequest],
):
    tracing_client.set_exchange(exchange=exchange)
    await tracing_client.fundings.list(request_)


@pytest.mark.parametrize("exchange", (constant.NYSE, constant.ASX))
@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_cash_available(
    tracing_client: stake.StakeClient,
    exchange: Union[constant.ASXUrl, constant.NYSEUrl],
):
    tracing_client.set_exchange(exchange)
    cash_available = await tracing_client.fundings.cash_available()
    assert cash_available.cash_available_for_withdrawal == 1000.0


@pytest.mark.parametrize("exchange", (constant.NYSE, constant.ASX))
@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_funds_in_flight(
    tracing_client: stake.StakeClient,
    exchange: Union[constant.ASXUrl, constant.NYSEUrl],
):
    tracing_client.set_exchange(exchange=exchange)
    await tracing_client.fundings.in_flight()
