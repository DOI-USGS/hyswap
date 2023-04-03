from importlib.metadata import version
from importlib.metadata import PackageNotFoundError

try:
    __version__ = version('hyswap')
except PackageNotFoundError:
    __version__ = "version-unknown"
