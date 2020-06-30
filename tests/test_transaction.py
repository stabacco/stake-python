import pytest

from stake import transaction


@pytest.mark.asyncio
async def test_list_transactions(test_client):
    request = transaction.TransactionRecordRequest()
    transactions = await test_client.transactions.list(request)

    import pprint

    for tr in transactions:
        pprint.pprint(tr.dict())
    assert len(transactions) == 1
