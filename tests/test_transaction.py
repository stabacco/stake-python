import pytest

from stake import transaction


@pytest.mark.asyncio
async def test_list_transactions(tracing_client):
    request = transaction.TransactionRecordRequest(limit=6)
    transactions = await tracing_client.transactions.list(request)

    assert len(transactions) == 6
