import asyncio
import sys

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from stake.client import StakeClient
from tests.vcr_scrubber import redact_sensitive_data, redact_sensitive_request

load_dotenv()


@pytest_asyncio.fixture
async def tracing_client(request, mocker):
    async with StakeClient() as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    if sys.version_info < (3, 10):
        loop = asyncio.get_event_loop()
    else:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()

        asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            "stake-session-token",
            ("authorization", "REDACTED"),
        ],
        "before_record_request": redact_sensitive_request,
        "before_record_response": redact_sensitive_data,
    }
