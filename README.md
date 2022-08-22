[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
![Coverage](coverage.svg)[![Downloads](https://pepy.tech/badge/stake)](https://pepy.tech/project/stake)[![Downloads](https://pepy.tech/badge/stake/month)](https://pepy.tech/project/stake)

# Stake

**Stake** is an unofficial Python client for the [Stake](https://hellostake.com) trading platform.

This library wraps the current Stake api and allows common trade operations, such as submitting buy/sell requests, checking your portfolio etc...

Please note that, at the current stage, the Stake client is asynchronous.

## Installation

```$
pip install stake
```

## Quickstart

After you install the package, you will need to authenticate to Stake in order to get authorization to interact with your account.
In order to successfully issue requests to the Stake platform you will need to authenticate to it. Every requests to the Stake endpoints will need to contain a `Stake-Session-Token` in the request headers.

## Using an existing Session-Token

You can retrieve one of these `Stake-Session-Token` by using the developer tools in your browser (Network tab) and inspecting some of the request headers sent to some of the `https://global-prd-api.hellostake.com/` host. (For example, click on the wishlist of dashboard links to see some session-token authenticated requests)

They are usually valid for 30 days (be sure to enable that checkbox on login) and seem to get refreshed before expiry so you should be good to use them directly.

If you already have an existing token you can pass it on to the `StakeClient` as such:

```python

from stake import StakeClient, SessionTokenLoginRequest, CredentialsLoginRequest
import asyncio

login_request = SessionTokenLoginRequest()
async def print_user():
    async with StakeClient(login_request) as stake_session:
        print(stake_session.user.first_name)
        print(stake_session.headers.stake_session_token)

asyncio.run(print_user())
```

> **_NOTE:_** The default value of the token is read from the `STAKE_TOKEN` environment variable. If you have that env-var set you should be able to just use:
> `async with StakeClient() as stake_session: ...`

## Login with your credentials

If you prefer to pass in your username/password credentials to login instead, it's easy to do:

### If you do not have two-factor authentication enabled

```python

from stake import StakeClient, SessionTokenLoginRequest, CredentialsLoginRequest
import asyncio

login_request = CredentialsLoginRequest(
    username="youruser@name.com", # os.getenv("STAKE_USER") by default
    password="yoursecretpassword") # os.getenv("STAKE_PASS") by default

async def print_user(request: CredentialsLoginRequest):
    async with StakeClient(request) as stake_session:
        print(stake_session.user.first_name)
        print(stake_session.headers.stake_session_token)

asyncio.run(print_user(login_request))
```

### If you have two-factor authentication enabled

In this case you need to have your phone around, get the current code from the authenticator app and add it to the `CredentialsLoginRequest` as such:

```python
    login_request = CredentialsLoginRequest(username="youruser@name.com",password="yoursecretpassword",
        otp="Your-authenticator-app-code")
```

Obviously, this can become a bit inconvenient, since you will need to provide the otp code every time you instantiate a new `StakeClient` instance. Therefore, you could probably authenticate once with your credentials, retrieve the session token from the headers(`stake_session.headers.stake_session_token`), and store it in the `STAKE_TOKEN` env-var for subsequent usages.

## Choose your trading exchange

Stake can currently trade on the NY stock exchange (default for this library) as well as the Australian ASX. In order to choose which trading market to use you can initialize the client by specifying the `exchange` argument:

```python
import asyncio
from typing import Union

import stake


async def show_current_orders(
    current_exchange: Union[stake.constant.ASXUrl, stake.constant.NYSEUrl]
):
    async with stake.StakeClient(exchange=current_exchange) as stake_session:
        my_equities = await stake_session.orders.list()
        return my_equities

# ASX
print(asyncio.run(show_current_orders(stake.ASX)))

# NYSE
print(asyncio.run(show_current_orders(stake.NYSE)))

```

Alternatively you can call the `set_exchange` method on the `StakeClient` object.

One thing to note, is that the apis for the two exchanges are currently wildly different, and this reflects in some parts of this library as well.
You might find that the way you need to perform a trade (as well as the resulting response) is somewhat different when switching between exchanges.

As a rule of thumb the code for the ASX stake api resides in the `stake.asx` python package
while the one for the USA one is under the main `stake` namespace (for backwards compatibitity mostly, it might get moved to `stake.nyse` in the future).

## Examples

With `stake-python` you can do most of the operations that are available through the web app.

Here are some examples:

### Display the contents of your portfolio

```python
import stake
import asyncio
from stake.constant import NYSE

async def show_portfolio():
    # here the client will use the STAKE_TOKEN env var for authenticating
    async with stake.StakeClient(exchange=NYSE) as stake_session:
        my_equities = await stake_session.equities.list()
        for my_equity in my_equities.equity_positions:
            print(my_equity.symbol, my_equity.yearly_return_value)
        return my_equities

asyncio.run(show_portfolio())
```

Which will return something like:

```bash
AAPL 80.48
ADBE 251.35
GOOG 559.89
GRPN -13.77
HTZ -10.52
MSFT 97.14
NFLX 263.55
NIO 17.3
NVDA 410.04
OKTA 96.31
SHOP 690.68
SPOT 142.88
SQ 101.75
TQQQ 115.82
TSLA 402.37
VGT 130.08
ZM 331.1
```

### Buy/Sell shares

You can send buy/sell orders to the platform quite easily by just issuing trade requests.
Please check the `stake.trade` module for more details.

```python

import asyncio
import stake

async def example_limit_buy():
    symbol = "TSLA"
    async with stake.StakeClient() as stake_session:
        return await stake_session.trades.buy(
            stake.LimitBuyRequest(symbol=symbol, limitPrice=10, quantity=1000)
        )

asyncio.run(example_limit_buy())
```

To perform multiple requests at once you can use an `asyncio.gather` operation to run all the buy trades in parallel.

```python

import asyncio
import stake

async def example_stop_sell(symbol='TSLA'):
    """THis example will add a stop sell request for one of your equities"""
    async with stake.StakeClient() as stake_session:
        my_equities = await stake_session.equities.list()
        tsla_equity = [equity for equity in my_equities.equity_positions if equity.symbol == symbol][0]
        stop_price = round(tsla_equity.market_price - 0.025 * tsla_equity.market_price)
        stop_sell_request = stake.StopSellRequest(symbol=tsla_equity.symbol,
                                                  stopPrice=stop_price,
                                                  comment="My stop sell.",
                                                  quantity=tsla_equity.available_for_trading_qty)
        return await stake_session.trades.sell(request=stop_sell_request)

asyncio.run(example_stop_sell('MSFT'))
```

### Watchlists

These are some examples on how to interact with watchlists:

```python
import stake
import asyncio
from stake.watchlist import Watchlist

async def create_watchlist(name: str) -> "Watchlist":
    async with stake.StakeClient() as stake_session:
        request= stake.CreateWatchlistRequest(name = name)
        new_watchlist = await stake_session.watchlist.create_watchlist(request=request)
        return new_watchlist

asyncio.run(create_watchlist(name='My watchlist'))
```

```python
import stake
import asyncio
from stake.watchlist import Watchlist

async def update_watchlist(id: str, tickers: "List[str]") -> "Watchlist":
    async with stake.StakeClient() as stake_session:
        request= stake.UpdateWatchlistRequest(id=id, tickers=tickers)
        watchlist = await stake_session.watchlist.add_to_watchlist(request=request)
        return watchlist

asyncio.run(update_watchlist(id=WATCHLIST_ID, tickers=["TSLA", "MSFT", "GOOG"] ))
```

```python
import stake
import asyncio
from stake.watchlist import Watchlist

async def remove_from_watchlist(id: str, tickers: "List[str]") -> "Watchlist":
    async with stake.StakeClient() as stake_session:
        request= stake.UpdateWatchlistRequest(id=id, tickers=tickers)
        watchlist = await stake_session.watchlist.remove_from_watchlist(request=request)
        return watchlist

asyncio.run(remove_from_watchlist(id=WATCHLIST_ID, tickers=["TSLA", "GOOG"] ))

```

```python
import stake
import asyncio
from stake.watchlist import Watchlist

async def delete_watchlist(id: str) -> "Watchlist":
    async with stake.StakeClient() as stake_session:
        request= stake.DeleteWatchlistRequest(id=id)
        watchlist = await stake_session.watchlist.delete_watchlist(request=request)
        return watchlist

asyncio.run(delete_watchlist(id=WATCHLIST_ID))

```

For more examples, you can have a look at the unittests.

## Contributors

### Contributors on GitHub

- [Contributors](https://github.com/stabacco/stake-python/graphs/contributors)

## License

- see [LICENSE](https://github.com/stabacco/stake-python/blob/master/LICENSE.md) file

## Contact

- Created by [Stefano Tabacco](https://github.com/stabacco)
