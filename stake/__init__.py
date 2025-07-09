# flake8: noqa
from pathlib import Path

from single_version import get_version

from .client import *  # noqa: F401, F403
from .common import *  # noqa: F401, F403
from .constant import *  # noqa: F401, F403
from .funding import *  # noqa: F401, F403
from .fx import *  # noqa: F401, F403
from .market import *  # noqa: F401, F403
from .order import *  # noqa: F401, F403
from .product import *  # noqa: F401, F403
from .ratings import *  # noqa: F401, F403
from .statement import *  # noqa: F401, F403
from .trade import *  # noqa: F401, F403
from .transaction import *  # noqa: F401, F403
from .watchlist import *  # noqa: F401, F403

__version__ = get_version("stake", Path(__file__).parent.parent)
