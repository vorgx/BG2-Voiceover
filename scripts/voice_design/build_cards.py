"""Draft character cards from sanitized line data.

This script is a light-weight implementation inspired by the starter-kit blueprint.
It reads the configured lines CSV, extracts the first few sample lines for each
speaker, infers simple traits, and writes `data/character_cards.json`.

The heuristics are intentionally conservative so they do not overwrite any
hand-authored content. If `data/character_cards.json` already exists a backup is
created alongside the new file.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime
from importlib import import_module
from pathlib import Path
from typing import Dict, Iterable, List

import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

config_mod = import_module("bg2vo.config")
lines_mod = import_module("bg2vo.lines")

load_config = config_mod.load_config
CONFIG_ROOT = config_mod.ROOT
LineRecord = lines_mod.LineRecord
load_lines = lines_mod.load_lines

LINES_CSV = ROOT / "data" / "lines.csv"
OUTPUT_JSON = ROOT / "data" / "character_cards.json"
BACKUP_DIR = ROOT / "data" / "backups"

SAMPLE_LIMIT = 5

# Keyword heuristics adapted from the blueprint document
ARCHETYPE_PATTERNS = {
    "cheery": re.compile(r"\b(cheer|playful|bubbly|bright|friendly|optimistic)\b", re.I),
    "stoic": re.compile(r"\b(stoic|stern|duty|honou?r|disciplined|soldier)\b", re.I),
    "sardonic": re.compile(r"\b(sarcastic|sardonic|dry|acerbic|snide)\b", re.I),
    "mystic": re.compile(r"\b(mystic|prophecy|arcane|seer|vision)\b", re.I),
}


def _resolve_lines_csv() -> Path:
    try:
        settings = load_config()
    except Exception as exc:  # pragma: no cover - defensive fallback
        print(f"⚠️ Falling back to {LINES_CSV} (config load failed: {exc})")
        return LINES_CSV

    configured = settings.inputs.get("lines_csv")
    if not configured:
        return LINES_CSV

    candidate = Path(configured)
    if not candidate.is_absolute():
        root_hint = settings.paths.get("repo_root")
        base = Path(root_hint) if root_hint else CONFIG_ROOT
        candidate = base / candidate
    return candidate


def _gather_samples(rows: Iterable[LineRecord]) -> Dict[str, List[LineRecord]]:
    samples: Dict[str, List[LineRecord]] = defaultdict(list)
    for row in rows:
        if not row.speaker or not row.text:
            continue
        bucket = samples[row.speaker]
        if len(bucket) >= SAMPLE_LIMIT:
            continue
        bucket.append(row)
    return samples


def _estimate_energy(texts: List[str]) -> str:
    if not texts:
        return "medium"
    lengths = [len(t.split()) for t in texts]
    avg_len = sum(lengths) / max(len(lengths), 1)
    exclamations = sum(t.count("!") for t in texts)
    if exclamations >= 2 or avg_len <= 7:
        return "high"
    if avg_len >= 18:
        return "low"
    return "medium"


def _infer_archetype(texts: List[str]) -> str | None:
    joined = " ".join(texts)
    for archetype, pattern in ARCHETYPE_PATTERNS.items():
        if pattern.search(joined):
            return archetype
    return None


def _derive_traits(texts: List[str]) -> Dict[str, str | None]:
    return {
        "energy": _estimate_energy(texts),
        "archetype": _infer_archetype(texts),
    }


def write_cards() -> Path:
    lines_path = _resolve_lines_csv()
    if not lines_path.exists():
        raise FileNotFoundError(f"Cannot find master lines CSV: {lines_path}")

    samples = _gather_samples(load_lines(lines_path))

    cards = {}
    for speaker, entries in sorted(samples.items()):
        texts = [item.text for item in entries]
        traits = _derive_traits(texts)
        cards[speaker] = {
            "sources": [f"{lines_path.name} (first {len(entries)} entries)"],
            "traits": traits,
            "lines": [int(item.line_id) for item in entries if item.line_id and item.line_id.isdigit()],
            "notes": "auto-generated draft",
        }

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if OUTPUT_JSON.exists():
        backup_path = BACKUP_DIR / f"character_cards_{datetime.now():%Y%m%d_%H%M%S}.json"
        backup_path.write_text(OUTPUT_JSON.read_text(encoding="utf-8"), encoding="utf-8")

    OUTPUT_JSON.write_text(json.dumps(cards, indent=2, ensure_ascii=False), encoding="utf-8")
    return OUTPUT_JSON


def main() -> None:
    output = write_cards()
    print(f"Drafted character cards → {output}")
    print("Review traits manually before relying on them for voice presets.")


if __name__ == "__main__":
    main()
