import pytest

from stake import CredentialsLoginRequest
from stake import SessionTokenLoginRequest
from stake import StakeClient
from stake.client import InvalidLoginException, StakeSession


@pytest.mark.asyncio
async def test_invalid_login(tracing_client):
    request = CredentialsLoginRequest(
        username="unknown@user.com", password="WeirdPassword"
    )
    with pytest.raises(InvalidLoginException):
        await StakeClient(request=request)

    request = SessionTokenLoginRequest(token="invalidtoken002")
    with pytest.raises(InvalidLoginException):
        await StakeClient(request=request)

@pytest.mark.asyncio
async def test_contextmanager(tracing_client):
    request = CredentialsLoginRequest(
        username="tabacco.stefano@gmail.com", password="Stegala74"
    )
    async with StakeSession(request=request) as client:
        print(client)
