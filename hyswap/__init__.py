from importlib.metadata import version
from importlib.metadata import PackageNotFoundError
from hyswap.utils import *  # noqa
from hyswap.exceedance import *  # noqa

try:
    __version__ = version('hyswap')
except PackageNotFoundError:
    __version__ = "version-unknown"
