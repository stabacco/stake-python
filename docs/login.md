In order to successfully issue  requests to the Stake api endpoints you will need to submit, with every request that need authorization, a `Stake-Session-Token` in the request headers.

## Using an existing Session Token

You can retrieve one of these `Stake-Session-Token` by using the developer tools in your browser for example and inspecting some of the request headers sent to some of the `https://global-prd-api.hellostake.com/` host.

They are usually valid for 30 days and seem to get refreshed before expiry so you should be good to use them directly.

If you already have an existing token you can pass it on to the `StakeClient` as such:
```python

from stake import StakeClient, SessionTokenLoginRequest, CredentialsLoginRequest
import asyncio

login_request = SessionTokenLoginRequest(token="secrettoken")
async def print_user():
    async with StakeClient(login_request) as stake_session:
        print(stake_session.user.first_name)
        print(stake_session.headers.stake_session_token)

asyncio.run(print_user())
```

> **_NOTE:_**  The default value of the token can be read from an environment variable named `STAKE_TOKEN`.


## Login with your credentials

If you prefer to pass in your username/password credentials to login it's easy to do:

### If you do not have two-factor authentication enabled:

```python

from stake import StakeClient, SessionTokenLoginRequest, CredentialsLoginRequest
import asyncio

login_request = CredentialsLoginRequest(username="youruser@name.com",password="yoursecretpassword")

async def print_user():
    async with StakeClient(login_request) as stake_session:
        print(stake_session.user.first_name)

asyncio.run(print_user())
```

### If you have two-factor authentication enabled:

In this case you have to have your phone around, get the current code from the authenticator app and write it in the login request as such:
```python
    login_request = CredentialsLoginRequest(username="youruser@name.com",password="yoursecretpassword",
        otp="Your-authenticator-app-code")
```

Obviously, this can become a bit inconvenient, since you will need to provide the otp code every time you instantiate a new `StakeClient` instance. Therefore, you could probably authenticate once with your credentials, retrieve the session token from the headers, and save it in the `STAKE_TOKEN` env-var for subsequent usages.
