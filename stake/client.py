import asyncio
import os
from urllib.parse import urljoin

from aiohttp_requests import requests
from dotenv import load_dotenv

STAKE_URL = "https://prd-api.stake.com.au/api/"


load_dotenv()


def today() -> str:
    """returns the date of today

    Returns:
        [type]: [description]
    """
    from arrow import now

    n = now()
    return n.format("DD/MM/YYYY")


def last_year():
    from arrow import now

    n = now()
    return n.shift(years=-1).format("DD/MM/YYYY")


class StakeClient:
    def __init__(self):
        self.user = None

        self.headers = {
            "Accept": "application/json",
            "Host": "prd-api.stake.com.au",
            "Origin": "https://stake.com.au",
            "Referer": "https://stake.com.au/dashboard/portfolio",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Content-Type": "application/json",
        }

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
        json_data = await response.json()
        self.user = json_data
        self.headers["Stake-Session-Token"] = self.user["sessionKey"]
        return json_data

    async def get_fundings(self, startDate: str = None, endDate: str = None) -> dict:
        startDate = startDate or last_year()
        endDate = endDate or today()
        url = self._url("utils/activityLog/fundingOnly")
        payload = {"endDate": endDate, "startDate": startDate}
        print(payload)
        response = await requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return await response.json()

    async def get_funds_in_flight(self) -> dict:

        url = self._url("/fund/details")
        response = await requests.get(url, headers=self.headers, json={})
        response.raise_for_status()
        return response.json()

    async def get_equities(self):
        url = self._url("/users/accounts/equityPositions")
        response = requests.get(url, headers=self.headers, json={})
        response.raise_for_status()
        return response.json()

    async def sell_order(self):
        {
    "userId": self.user[],
    "itemId": "a45b1c39-d1a4-4a90-a388-c34b1257503a",
    "itemType": "instrument",
    "orderType": "stop",
    "quantity": "8.16321243",
    "stopPrice": "4.9",
    "limitPrice": "",
    "comments": ""
}


def main():
    loop = asyncio.get_event_loop()
    client = StakeClient()
    response = asyncio.run(client.login())
    print(client.user)
    response = asyncio.run(client.get_fundings())
    print(response)
    # print(client.user)
    # asyncio.run(client.get_fundings())
    # response = loop.run_until_complete(client.get_fundings())
    # print(client.user)


if __name__ == "__main__":
    main()
