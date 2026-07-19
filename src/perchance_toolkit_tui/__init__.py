"""perchance TUI — terminal user interface for perchance.org."""

from importlib.metadata import version

try:
    __version__ = version("perchance-toolkit")
except Exception:
    __version__ = "0.1.0"
