from importlib.metadata import version
from importlib.metadata import PackageNotFoundError
from hyswap.utils import *  # noqa
from hyswap.exceedance import *  # noqa
from hyswap.rasterhydrograph import *  # noqa
from hyswap.percentiles import *  # noqa
from hyswap.cumulative import *  # noqa
from hyswap.plots import *  # noqa
from hyswap.similarity import *  # noqa
from hyswap.runoff import *  # noqa

try:
    __version__ = version('hyswap')
except PackageNotFoundError:
    __version__ = "version-unknown"
