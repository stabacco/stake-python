# Usage examples

With `stake-python` you can do most of the operations that are available through the web app.


Here are some examples:

## Display the contents of your portfolio

```python
from stake import StakeClient, SessionTokenLoginRequest, CredentialsLoginRequest
import asyncio


async def show_portfolio():
    # here the client will use the STAKE_TOKEN env var for authenticating
    async with StakeClient() as stake_session:
        my_equities = await stake_session.equities.list()

        for my_equity in my_equities.equity_positions:
            print(my_equity.symbol, my_equity.yearly_return_value)

        return my_equities

asyncio.run(show_portfolio())
```

Which will return something like:
```
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

## Buy/Sell shares

You can send buy/sell orders to the platform quite easily by just issuing trade requests.
Please check the `stake.trade` module for more details.

```python

async def example_limit_buy():
    symbol = "UNKN" # should be the equity symbol, for ex: AAPL, TSLA, GOOGL
    async with StakeClient() as stake_session:
        return trades.buy(
            LimitBuyRequest(symbol=symbol, limitPrice=10, quantity=1000)
        )

asyncio.run(example_limit_buy())
```

To perform multiple requests at once you can use an `asyncio.gather` operation to run all the buy trades in parallel.



```python


async def example_stop_sell():
    """THis example will add a stop sell request for one of your equities"""
    my_equities = await show_portfolio()

    symbol = "T.SLA" # mispelt on purpose so that no trade actually happens, should be TSLA.
    tsla_equity = [equity for equity in my_equities.equity_positions if equity.symbol == symbol]


    stop_sell_request = stake.StopSellRequest(symbol=tsla_equity.symbol,
                                                  stopPrice=stop_price,
                                                  comment="My stop sell.",
                                                  quantity=current_equity.available_for_trading_qty)
        result = await stake_client.trades.sell(request=stop_sell_request)
    symbol = "UNKN" # should be the equity symbol, for ex: AAPL, TSLA, GOOGL
    async with StakeClient() as stake_session:
        return trades.buy(
            LimitBuyRequest(symbol=symbol, limitPrice=10, quantity=1000)
        )

asyncio.run(example_limit_buy())
```
