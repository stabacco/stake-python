import weakref
from enum import Enum
from functools import partial
from typing import TYPE_CHECKING

import inflection

if TYPE_CHECKING:
    from stake.client import StakeClient

camelcase = partial(inflection.camelize, uppercase_first_letter=False)

__all__ = ["SideEnum"]


class SideEnum(str, Enum):
    BUY = "B"
    SELL = "S"


class BaseClient:
    # flake8: noqa
    def __init__(self, client: "StakeClient"):
        self._client = weakref.proxy(client)
