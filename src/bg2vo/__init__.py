"""BG2 Voiceover helper package.

This package wraps a subset of the repository's scripts in a module-friendly
form so that future CLI tooling can leverage them without touching the legacy
scripts. The initial implementation focuses on introspection utilities.
"""
from __future__ import annotations

from .config import load_config  # noqa: F401
from .lines import load_lines  # noqa: F401
from .voices import load_voices  # noqa: F401
from .audit import count_lines  # noqa: F401

__all__ = [
    "load_config",
    "load_lines",
    "load_voices",
    "count_lines",
]
