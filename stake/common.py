import weakref
from enum import Enum
from functools import partial

import inflection

camelcase = partial(inflection.camelize, uppercase_first_letter=False)

__all__ = ["SideEnum"]


class SideEnum(str, Enum):
    BUY = "B"
    SELL = "S"


class BaseClient:
    # flake8: noqa
    def __init__(self, client: "stake._StakeClient"):  # type: ignore
        self._client = weakref.proxy(client)
