import json
from typing import List
from typing import Optional

from aiohttp_requests import requests
from pydantic import BaseModel
from pydantic import Field


class PostmanCollectionInfo(BaseModel):
    _postman_id: str = "f175f235-0eb7-4e9b-b6ee-57de3865612b"
    name: str
    description: str = "Postman collection"
    schema_: str = Field(
        "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        alias="schema",
    )


class PostmanCollectionRequestHeader(BaseModel):
    key: str
    value: str
    type: str = "text"


class PostmanCollectionRequestUrl(BaseModel):
    raw: str
    host: List[str] = "{{url}}"

    @property
    def path(self) -> list:
        return self.raw.replace(self.host[0] + "/", "").split("/")

    def dict(self, *args, **kwargs):
        dict_ = super().dict(*args, **kwargs)
        dict_["path"] = self.path
        return dict_


class PostmanCollectionRequestBody(BaseModel):
    mode: str = "raw"
    raw: str  # json-encoded


class PostmanCollectionRequest(BaseModel):
    name: str = None
    method: str
    header: List[PostmanCollectionRequestHeader]
    url: PostmanCollectionRequestUrl
    description: str
    body: Optional[PostmanCollectionRequestBody]


class PostmanCollectionResponse(BaseModel):
    name: str
    originalRequest: PostmanCollectionRequest = None
    status: str
    code: int
    _postman_previewlanguage: str = "json"
    header: List[PostmanCollectionRequestHeader]
    cookie: list = []
    body: str  # json-encoded.
    variable: list = []  # no variables atm
    protocolProfileBehavior: dict = {}
    id: str = None


class PostmanCollectionItem(BaseModel):
    name: str
    _postman_id: str = None
    request: PostmanCollectionRequest
    response: List[PostmanCollectionResponse]


class PostmanCollection(BaseModel):
    info: PostmanCollectionInfo
    item: List[PostmanCollectionItem]


async def upload_postman_collection(
    collection: PostmanCollection, postman_collection_id: str, postman_api_key: str
) -> dict:
    response = await requests.put(
        f"https://api.getpostman.com/" f"collections/{postman_collection_id}",
        headers={"Content-Type": "application/json", "X-Api-Key": postman_api_key},
        data=json.dumps({"collection": collection.dict(by_alias=True)}),
    )
    response.raise_for_status()
    print(f"Updated collection {postman_collection_id}")
    return await response.json()


async def get_mocks(postman_api_key: str):
    response = await requests.get(
        "https://api.getpostman.com/mocks",
        headers={"Content-Type": "application/json", "X-Api-Key": postman_api_key},
    )
    response.raise_for_status()
    return await response.json()


async def get_collection(postman_api_key, collection_id):
    url = f"https://api.getpostman.com/collections/{collection_id}"

    payload = {}
    files = {}
    headers = {"Content-Type": "application/json", "X-Api-Key": postman_api_key}

    response = await requests.get(url, headers=headers)
    data = await response.json()
    return PostmanCollection(**data["collection"])


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    key = os.getenv("STAKE_POSTMAN_MOCK_API_KEY_UNITTEST")
    collection_id = os.getenv("STAKE_POSTMAN_UNITTEST_COLLECTION_ID")
    import asyncio

    collection = asyncio.run(get_collection(key, collection_id))
    print(collection)
