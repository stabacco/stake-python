import json
import sys

import pkg_resources
import pytest
from aioresponses import aioresponses

from stake.constant import STAKE_URL
from stake.funding import FundingRequest
from tests.conftest import fixtures_response


@pytest.mark.asyncio
async def test_list_fundings(tracing_client, fixtures_response):
    fundings = await tracing_client.fundings.list(FundingRequest())
    assert len(fundings) == 2


@pytest.mark.asyncio
async def test_cash_available(tracing_client, fixtures_response):
    cash_available = await tracing_client.fundings.cash_available()
    assert cash_available.cash_available_for_withdrawal == 551.14
    assert cash_available.cash_settlement[0].utc_time.month == 9


"""
write_data = {
                "url": "{url}" + Url.cash_available,
                "body": None,
                "payload": data,
                "method": "GET",
        }
        import json;json.dump(write_data, open("cash_available.json", "w"))
        """
