import asyncio

import pytest

from stake.client import StakeClient


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_client():
    return await StakeClient()
