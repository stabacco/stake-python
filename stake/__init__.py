# flake8: noqa
from pathlib import Path

from single_version import get_version

from .client import *
from .common import *
from .funding import *
from .fx import *
from .market import *
from .order import *
from .product import *
from .ratings import *
from .trade import *
from .transaction import *
from .watchlist import *

__version__ = get_version("stake", Path(__file__).parent.parent)
