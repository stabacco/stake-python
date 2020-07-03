import pytest


@pytest.mark.asyncio
async def test_how_transactions(test_client_fixture_generator):
    from stake import transaction

    request = transaction.TransactionRecordRequest(limit=6)
    return await test_client_fixture_generator.transactions.list(request)


@pytest.mark.asyncio
async def test_show_portfolio(test_client_fixture_generator):
    return await test_client_fixture_generator.equities.list()


@pytest.mark.asyncio
async def test_show_pending_orders(test_client_fixture_generator):
    return await test_client_fixture_generator.orders.list()


@pytest.mark.asyncio
async def test_show_fundings(test_client_fixture_generator):
    from stake.funding import FundingRequest

    request = FundingRequest()
    return await test_client_fixture_generator.fundings.list(request=request)


@pytest.mark.asyncio
async def test_add_stop_sell_for_every_equity_if_loses_5_percent(
    test_client_fixture_generator,
):
    owned_equities = await test_client_fixture_generator.equities.list()
    for equity in owned_equities.equityPositions:
        import pprint

        pprint.pprint(equity.dict())
        print(
            equity.name,
            equity.unrealizedPL,
            equity.lastTrade,
            100 * equity.unrealizedPL / equity.marketValue,
        )
