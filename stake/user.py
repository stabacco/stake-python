from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic.fields import Field

from stake.common import camelcase


class User(BaseModel):
    id: str = Field(alias="userId")
    first_name: str
    last_name: str
    email_address: str
    mac_status: str
    account_type: str
    region_identifier: str
    dw_account_number: Optional[str] = Field(None, alias="dw_AccountNumber")
    can_trade_on_unsettled_funds: Optional[bool] = None
    username: Optional[str] = None
    model_config = ConfigDict(alias_generator=camelcase, populate_by_name=True)
