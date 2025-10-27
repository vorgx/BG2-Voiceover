"""Suggest voice presets based on character card traits.

This script is intentionally non-destructive. It reads
`data/character_cards.json`, applies a lightweight trait → preset map, and
prints recommendations. The output can optionally be merged into
`config/voices.sample.json` by passing `--write`.
"""
from __future__ import annotations

import argparse
import json
from importlib import import_module
from pathlib import Path
from typing import Dict

import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

config_mod = import_module("bg2vo.config")
voices_mod = import_module("bg2vo.voices")

load_config = config_mod.load_config
CONFIG_ROOT = config_mod.ROOT
load_voices = voices_mod.load_voices

CARDS_JSON = ROOT / "data" / "character_cards.json"
VOICES_SAMPLE = ROOT / "config" / "voices.sample.json"

PRESET_RULES = {
    ("cheery", "high"): {"voice": "female_lighthearted", "speed": 0.04, "pitch": 0.12},
    ("stoic", "medium"): {"voice": "female_determined", "speed": -0.03, "pitch": -0.05},
    ("sardonic", "medium"): {"voice": "male_rogue", "speed": -0.02, "pitch": -0.02},
    (None, "high"): {"voice": "narrator", "speed": 0.02, "pitch": 0.04},
    (None, "low"): {"voice": "narrator", "speed": -0.02, "pitch": -0.02},
}


def _resolve_cards_path() -> Path:
    try:
        settings = load_config()
    except Exception as exc:  # pragma: no cover - defensive fallback
        print(f"⚠️ Falling back to {CARDS_JSON} (config load failed: {exc})")
        return CARDS_JSON

    configured = settings.outputs.get("cards_json") if hasattr(settings, "outputs") else None
    if not configured:
        return CARDS_JSON

    candidate = Path(configured)
    if not candidate.is_absolute():
        root_hint = settings.paths.get("repo_root")
        base = Path(root_hint) if root_hint else CONFIG_ROOT
        candidate = base / candidate
    return candidate


def _resolve_voices_path() -> Path:
    try:
        settings = load_config()
    except Exception as exc:  # pragma: no cover
        print(f"⚠️ Falling back to {VOICES_SAMPLE} (config load failed: {exc})")
        return VOICES_SAMPLE

    configured = settings.inputs.get("voices_json") if hasattr(settings, "inputs") else None
    if not configured:
        configured = settings.outputs.get("voices_sample") if hasattr(settings, "outputs") else None
    if not configured:
        return VOICES_SAMPLE

    candidate = Path(configured)
    if not candidate.is_absolute():
        root_hint = settings.paths.get("repo_root")
        base = Path(root_hint) if root_hint else CONFIG_ROOT
        candidate = base / candidate
    return candidate


def load_cards() -> Dict[str, Dict]:
    cards_path = _resolve_cards_path()
    if not cards_path.exists():
        raise FileNotFoundError(
            f"Character cards not found. Generate them via scripts/build_cards.py (expected at {cards_path})."
        )
    return json.loads(cards_path.read_text(encoding="utf-8"))


def pick_preset(archetype: str | None, energy: str | None) -> Dict[str, float | str]:
    key = (archetype, energy)
    if key in PRESET_RULES:
        return PRESET_RULES[key]
    # fallback on archetype only
    key = (archetype, None)
    if key in PRESET_RULES:
        return PRESET_RULES[key]
    # final fallback
    return {"voice": "narrator", "speed": 0.0, "pitch": 0.0}


def merge_into_sample(recommendations: Dict[str, Dict[str, float | str]]) -> None:
    voices_path = _resolve_voices_path()
    existing: Dict[str, Dict[str, float | str]] = {}
    if voices_path.exists():
        loaded = load_voices(voices_path)
        existing = {name: preset.to_dict() for name, preset in loaded.items()}
    existing.update(recommendations)
    voices_path.parent.mkdir(parents=True, exist_ok=True)
    voices_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")


def main(write: bool = False) -> None:
    cards = load_cards()
    recommendations: Dict[str, Dict[str, float | str]] = {}
    for speaker, card in sorted(cards.items()):
        traits = card.get("traits") or {}
        preset = pick_preset(traits.get("archetype"), traits.get("energy"))
        recommendations[speaker] = preset

    print("Suggested presets (trait-based):")
    for speaker, preset in recommendations.items():
        print(f"- {speaker}: {preset}")

    if write:
        merge_into_sample(recommendations)
        print(f"Merged recommendations into {_resolve_voices_path()}")
    else:
        print("Run with --write to update config/voices.sample.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build voice preset recommendations.")
    parser.add_argument("--write", action="store_true", help="Persist recommendations into voices.sample.json")
    args = parser.parse_args()
    main(write=args.write)
