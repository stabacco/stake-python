import pytest

from stake import transaction


@pytest.mark.asyncio
async def test_list_transactions(test_client):
    request = transaction.TransactionRecordRequest()
    transactions = await test_client.transactions.list(request)
    assert len(transactions) == 1
