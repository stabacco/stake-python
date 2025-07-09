from datetime import date

import pytest

import stake
from stake import StatementRequest


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_list_statements(tracing_client: stake.StakeClient):
    request = StatementRequest(
        symbol="CVNA", start_date=date(year=2022, month=1, day=1)
    )
    ratings = await tracing_client.statements.list(request)
    assert len(ratings) > 1


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_list_statements_unknown(tracing_client: stake.StakeClient):
    request = StatementRequest(
        symbol="__X_X", start_date=date(year=2022, month=1, day=1)
    )
    ratings = await tracing_client.statements.list(request)
    assert len(ratings) == 0
