"""perchance GUI — desktop application for perchance.org."""

from importlib.metadata import version

try:
    __version__ = version("perchance")
except Exception:
    __version__ = "0.1.0"
