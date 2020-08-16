import pytest

from stake import transaction


@pytest.mark.asyncio
async def test_list_transactions(test_client_fixture_generator):
    request = transaction.TransactionRecordRequest(limit=7)
    transactions = await test_client_fixture_generator.transactions.list(request)

    assert len(transactions) == 6
