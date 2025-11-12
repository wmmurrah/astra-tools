"""
ASTRA Tools - Convert ASTRA research reports to Quarto and Markdown formats.

This package provides tools for converting JSON artifacts from ASTRA (astra.allen.ai)
into well-formatted Quarto (.qmd) and Markdown (.md) documents with proper bibliography
support.
"""

__version__ = "0.1.0"

from .converters.json_to_qmd import convert_json_to_qmd
from .converters.json_to_md import convert_json_to_markdown
from .bib.regenerate_keys import regenerate_bib_keys

__all__ = [
    "convert_json_to_qmd",
    "convert_json_to_markdown",
    "regenerate_bib_keys",
]
