# flake8: noqa
from pathlib import Path

from single_version import get_version

from .client import *
from .funding import *
from .fx import *
from .market import *
from .order import *
from .product import *
from .trade import *
from .transaction import *
from .watchlist import *

__version__ = get_version("awesome_name", Path(__file__).parent.parent)
