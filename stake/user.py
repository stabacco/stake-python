from functools import partial
from typing import Optional

import inflection
from pydantic import BaseModel
from pydantic.fields import Field

camelcase = partial(inflection.camelize, uppercase_first_letter=False)


class User(BaseModel):
    id: str = Field(alias="userId")
    first_name: str
    last_name: str
    email_address: str
    mac_status: str
    account_type: str
    region_identifier: str
    dw_account_number: Optional[str] = Field(alias="dw_AccountNumber")
    can_trade_on_unsettled_funds: Optional[bool]
    username: Optional[str]

    class Config:
        alias_generator = camelcase
