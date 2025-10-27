"""Configuration helpers for the BG2 Voiceover project."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]
DEFAULTS_YAML = ROOT / "config" / "defaults.yaml"

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - PyYAML optional
    yaml = None


@dataclass
class Settings:
    paths: Dict[str, str]
    index_tts: Dict[str, str]
    inputs: Dict[str, str]
    outputs: Dict[str, str]
    sanitization: Dict[str, str]
    synthesis: Dict[str, Any]
    weidu: Dict[str, str]


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    if yaml is None:
        raise RuntimeError("PyYAML is not installed. Install it or parse the YAML manually.")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_config(path: Path | None = None) -> Settings:
    raw = _load_yaml(path or DEFAULTS_YAML)
    return Settings(
        paths=raw.get("paths", {}),
        index_tts=raw.get("index_tts", {}),
        inputs=raw.get("inputs", {}),
        outputs=raw.get("outputs", {}),
        sanitization=raw.get("sanitization", {}),
        synthesis=raw.get("synthesis", {}),
        weidu=raw.get("weidu", {}),
    )
