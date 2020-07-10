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

    def dict(self, *args, **kwargs):
        dict_ = super().dict(*args, **kwargs)
        dict_["schema"] = dict_.pop("schema_")
        return dict_


class PostmanCollectionRequestHeader(BaseModel):
    key: str
    value: str
    type: str = "text"


class PostmanCollectionRequestUrl(BaseModel):
    raw: str
    host: str = "{{url}}"

    @property
    def path(self) -> list:
        return self.raw.replace(self.host + "/", "").split("/")

    def dict(self, *args, **kwargs):
        dict_ = super().dict(*args, **kwargs)
        dict_["path"] = self.path
        return dict_


class PostmanCollectionRequestBody(BaseModel):
    mode: str = "raw"
    raw: str  # json-encoded


class PostmanCollectionRequest(BaseModel):
    name: str
    method: str
    header: List[PostmanCollectionRequestHeader]
    url: PostmanCollectionRequestUrl
    description: str
    body: Optional[PostmanCollectionRequestBody]


class PostmanCollectionResponse(BaseModel):
    name: str
    originalRequest: PostmanCollectionRequest
    status: str
    code: int
    _postman_previewlanguage: str = "json"
    header: List[PostmanCollectionRequestHeader]
    cookie: list = []
    body: str  # json-encoded.
    variable: list = []  # no variables atm
    protocolProfileBehavior: dict = {}


class PostmanCollectionItem(BaseModel):
    name: str
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
        data=json.dumps({"collection": collection.dict()}),
    )
    response.raise_for_status()
    print(f"Updated collection {postman_collection_id}")
    return await response.json()
