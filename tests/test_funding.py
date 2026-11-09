from typing import Union

import pytest

import stake
from stake import constant
from stake.asx.funding import FundingRequest as ASXFundingRequest
from stake.funding import CashAvailable
from stake.funding import TransactionRecordRequest as NYSEFundingRequest

_CASH_PAYLOAD = {
    "cashBalance": 1000.0,
    "cashAvailableForTrade": 1000.0,
    "cashAvailableForWithdrawal": 0.0,
    "dwCashAvailableForWithdrawal": 1000.0,
    "liquidCash": 6000.0,
    "reservedCash": 5000.0,
    "pendingPoliAmount": 5000.0,
    "pendingOrdersAmount": 0.0,
    "pendingWithdrawals": 0.0,
    "cardHoldAmount": 0.0,
    "cashSettlement": [{"utcTime": "2026-01-15T14:30:00.001Z", "cash": 0.0}],
}


def test_cash_available_exposes_liquid_cash():
    """Trading capacity must survive parsing; it is not a withdrawal figure."""
    cash_available = CashAvailable.model_validate(_CASH_PAYLOAD)

    assert cash_available.liquid_cash == 6000.0
    assert cash_available.cash_balance == 1000.0


def test_cash_available_keeps_unknown_fields():
    """A field the provider adds next must be observable, not dropped silently."""
    cash_available = CashAvailable.model_validate(
        {**_CASH_PAYLOAD, "someFutureField": "x"}
    )

    assert cash_available.model_extra == {"someFutureField": "x"}


def test_cash_available_without_liquid_cash_still_parses():
    payload = {
        key: value for key, value in _CASH_PAYLOAD.items() if key != "liquidCash"
    }

    assert CashAvailable.model_validate(payload).liquid_cash is None


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
