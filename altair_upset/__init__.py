"""UpSet plots using Altair."""

from .config import upsetaltair_top_level_configuration
from .upset import UpSetAltair, UpSetVertical

__all__ = ["UpSetAltair", "UpSetVertical", "upsetaltair_top_level_configuration"]
