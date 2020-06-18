import asyncio
from urllib.parse import urljoin

from aiohttp_requests import requests

STAKE_URL = "https://prd-api.stake.com.au/api/"


def today():
    from arrow import now

    n = now()
    today = n.format("DD/MM/YYYY")
    return today


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
    def _url(endpoint):
        return urljoin(STAKE_URL, endpoint, allow_fragments=True)

    async def login(self, username, password):
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
        self.headers["Stake-Session-Token"] = self.user.sessionKey
        return json_data

    async def get_fundings(
        self, endDate=lambda *_: today(), startDate=lambda *_: last_year()
    ):
        url = self._url("utils/activityLog/fundingOnly")
        payload = {"endDate": today, "startDate": last_year}
        response = await requests.request(
            "POST", url, headers=self.headers, json=payload
        )
        response.raise_for_status()
        return await response.json()


# def get_funds_in_flight():
#     url = "https://prd-api.stake.com.au/api/fund/details"
#     response = requests.request("GET", url, headers=headers, json={})
#     response.raise_for_status()
#     data = response.json()
#     return data


def main():
    loop = asyncio.get_event_loop()
    client = StakeClient()
    response = asyncio.run(client.login("tabacco.stefano@gmail.com", "password"))
    print(client.user)
    # response = loop.run_until_complete(client.get_fundings())
    # print(client.user)


if __name__ == "__main__":
    main()
