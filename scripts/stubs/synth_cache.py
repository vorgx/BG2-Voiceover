"""Simple synthesis cache helper.

The cache stores a hash of the StrRef, sanitized text, and voice parameters so
unchanged lines can be skipped during re-renders. The class is standalone and
can be imported by both legacy scripts and future `bg2vo` modules.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict


class SynthCache:
    """MD5-based cache for synthesized lines."""

    def __init__(self, cache_path: Path) -> None:
        self.cache_path = cache_path
        if cache_path.exists():
            self._data: Dict[str, Dict[str, str]] = json.loads(cache_path.read_text(encoding="utf-8"))
        else:
            self._data = {}

    @staticmethod
    def make_key(strref: str, text: str, voice: Dict[str, object]) -> str:
        hasher = hashlib.md5()
        hasher.update(strref.encode("utf-8"))
        hasher.update(text.encode("utf-8"))
        for field in ("voice", "ref", "speed", "pitch"):
            if field in voice and voice[field] is not None:
                hasher.update(str(voice[field]).encode("utf-8"))
        return hasher.hexdigest()

    def has(self, key: str) -> bool:
        return key in self._data

    def record(self, key: str, output_path: Path) -> None:
        self._data[key] = {"output": str(output_path)}

    def save(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")
