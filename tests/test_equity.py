import pytest

import stake
from stake import constant


@pytest.mark.parametrize("exchange", (constant.NYSE, constant.ASX))
@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_list_equities(tracing_client: stake.StakeClient, exchange):

    tracing_client.set_exchange(exchange)
    equities = await tracing_client.equities.list()

    assert equities.__class__.__name__ == "EquityPositions"
    assert equities.equity_positions

    for e in equities.equity_positions:
        assert not (set(e.model_fields.keys()).difference(e.model_fields_set))
