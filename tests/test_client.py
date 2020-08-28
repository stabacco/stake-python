import pytest

from stake import CredentialsLoginRequest
from stake import SessionTokenLoginRequest
from stake import StakeClient
from stake.client import InvalidLoginException, StakeSession


@pytest.mark.asyncio
async def test_invalid_login(test_client_fixture_generator):
    request = CredentialsLoginRequest(
        username="tabacco.stefano@gmail.com", password="Stegala74"
    )
    with pytest.raises(InvalidLoginException):
        await StakeClient(request=request)

    request = SessionTokenLoginRequest(token="invalidtoken002")
    with pytest.raises(InvalidLoginException):
        await StakeClient(request=request)

@pytest.mark.asyncio
async def test_contextmanager(test_client_fixture_generator):
    request = CredentialsLoginRequest(
        username="tabacco.stefano@gmail.com", password="Stegala74"
    )
    async with StakeSession(request=request) as client:
        print(client)