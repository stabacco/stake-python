import pytest


@pytest.mark.asyncio
async def test_how_transactions(test_client_fixture_generator):
    from stake import transaction

    request = transaction.TransactionRecordRequest(limit=6)
    return await test_client_fixture_generator.transactions.list(request)


@pytest.mark.asyncio
async def test_show_portfolio(test_client_fixture_generator):
    from stake import transaction

    return await test_client_fixture_generator.equities.list()
