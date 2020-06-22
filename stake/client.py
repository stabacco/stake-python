import asyncio
import os
from typing import Optional, List
from urllib.parse import urljoin

from aiohttp_requests import requests
from dotenv import load_dotenv

import user, funding, equity

STAKE_URL = "https://prd-api.stake.com.au/api/"


load_dotenv()


def today() -> str:
    """returns the date of today

    Returns:
        [str]: the formatted date
    """
    from arrow import now

    n = now()
    return n.format("DD/MM/YYYY")


def last_year():
    from arrow import now

    n = now()
    return n.shift(years=-1).format("DD/MM/YYYY")


class _StakeClient:
    def __init__(self):
        self.user = None

    @staticmethod
    def _url(endpoint: str) -> str:
        """Generates an url

        Args:
            endpoint (str): the final part of the enpoint

        Returns:
            str: the full url
        """
        return urljoin(STAKE_URL, endpoint, allow_fragments=True)

    async def login(
        self,
        username: str = os.getenv("STAKE_USER"),
        password: str = os.getenv("STAKE_PASS"),
    ) -> dict:
        payload = {
            "username": username,
            "password": password,
            "rememberMeDays": "30",
        }
        response = await requests.post(
            self._url("sessions/createSession"), json=payload
        )
        response.raise_for_status()

        user_data = await response.json()
        self.user = user.User(**user_data)

        self.headers = {
            "Accept": "application/json",
            "Host": "prd-api.stake.com.au",
            "Origin": "https://stake.com.au",
            "Referer": "https://stake.com.au",
            "Stake-Session-Token": self.user.sessionKey,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Content-Type": "application/json",
        }
        return self.user

    async def get_fundings(
        self, start_date: str = None, end_date: str = None
    ) -> List[funding.Funding]:
        start_date = start_date or last_year()
        end_date = end_date or today()

        url = self._url("utils/activityLog/fundingOnly")
        payload = {"endDate": end_date, "startDate": start_date}
        response = await requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        data = await response.json()

        return [funding.Funding(**d) for d in data]

    async def get_funds_in_flight(self) -> dict:
        url = self._url("fund/details")
        response = await requests.get(url, headers=self.headers, json={})
        response.raise_for_status()
        return await response.json()

    async def get_equities(self):
        url = self._url("users/accounts/equityPositions")
        response = await requests.get(url, headers=self.headers, json={})
        response.raise_for_status()
        data = await response.json()
        return equity.EquityPositions(**data)

    async def get_market_status(self) -> dict:
        url = self._url("utils/marketStatus")
        response = await requests.get(url, headers=self.headers)
        response.raise_for_status()
        return await response.json()

    async def get_marked_data(self, symbols: List[str]) -> Optional[dict]:

            if not symbols:
                return None

            url = self._url(f"quotes/marketData/{'.'.join(symbols)}")

            response = await requests.get(url, headers=self.headers)
            response.raise_for_status()
            return await response.json()

    async def sell_order(self):
        {
            "userId": self.user.userID,
            "itemId": "a45b1c39-d1a4-4a90-a388-c34b1257503a",
            "itemType": "instrument",
            "orderType": "stop",
            "quantity": "8.16321243",
            "stopPrice": "4.9",
            "limitPrice": "",
            "comments": "",
        }

    async def download_report(self, request: ):
        {"dateStart": "2020-05-22T07:20:20.057Z",
         "dateEnd": "2020-06-22T07:20:20.057Z",
         "reportFormat": "XLS",
         "reportName": "OrderTrans"}

async def StakeClient(
    username: Optional[str] = os.getenv("STAKE_USER"),
    password: Optional[str] = os.getenv("STAKE_PASS"),
) -> _StakeClient:
    """ Returns a logged in _StakeClient.

    Args:
        username: the user's username (email)
        password: the user's password.

    Returns:
        an instance of the _StakeClient

    """
    c = _StakeClient()
    _ = await c.login(username, password)
    return c


async def main():

    client = await StakeClient()
    user = client.user
    print(user.sessionKey)
    fundings, funds_in_flight, equities = await asyncio.gather(client.get_fundings(),
                                                     client.get_marked_data(['AAPL']),
                                                     client.get_market_status())
    # print(client.user)
    return fundings, funds_in_flight, equities


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    fundings, in_flight, market_status = loop.run_until_complete(main())
    import pprint; pprint.pprint(market_status)
