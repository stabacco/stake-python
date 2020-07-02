import pytest


@pytest.mark.asyncio
async def test_generate_fixtures(test_client_fixture_generator):
    from stake import transaction

    request = transaction.TransactionRecordRequest(limit=6)
    return await test_client_fixture_generator.transactions.list(request)
