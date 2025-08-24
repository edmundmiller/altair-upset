"""UpSet plots using Altair."""

from .annotations import AnnotationSpec
from .config import upsetaltair_top_level_configuration
from .upset import UpSetAltair

__all__ = ["UpSetAltair", "upsetaltair_top_level_configuration", "AnnotationSpec"]
