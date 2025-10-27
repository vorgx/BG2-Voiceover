# Usage Guide

This guide explains how to run the current tooling along with the newly imported blueprint scaffold. Existing chapter scripts continue to work; the new CLI and scripts can be adopted gradually.

---

## Quick Start (Legacy Flow)

1. Export `.D` files with Near Infinity → `BG2 Files/Dialog Files/`.
2. Convert to StrRef CSVs:
   ```powershell
   py scripts\convert_d_to_csv.py
   ```
3. Join with TLK text:
   ```powershell
   py scripts\near_infinity_join.py
   ```
4. Sanitize text (optional helper snippet in ../getting-started/CHAPTER_PIPELINE.md).
5. Run synthesis when ready:
   ```powershell
   py scripts\synth.py
   ```

---

## Blueprint Workflow

The starter-kit blueprint adds optional layers:

### Configuration
- Review `config/defaults.yaml` for environment paths.
- Update `config/voices.sample.json` when experimenting with presets.

### Character Preparation
- Draft cards (stub): `python scripts/build_cards.py`
- Derive presets (stub): `python scripts/build_refs.py`
- Optional pseudo references: `python scripts/gen_pseudorefs.py`

Currently these scripts emit TODO notes; they are placeholders for future automation and will not modify critical data unless explicitly instructed.

### CLI Entry Point

A minimal CLI wrapper can be invoked with:
```powershell
python -m bg2vo --help
```
It currently exposes safe informational commands (counts, env info). Additional verbs can be enabled as implementation matures.

---

## Voice Configuration

- Production mappings live in `data/voices.json`.
- Blueprint mappings live in `config/voices.sample.json`.
- Use `PRESETS.md` for guidance when tuning indexes.

---

## Reports & Logs

- Speaker counts: use snippet in `../getting-started/CHAPTER_PIPELINE.md`.
- Planned caches: `reports/synth-cache.json` (written when the cache helper is wired up).

---

## Staging & Installation

1. Stage audio under `mod/vvoBG/OGG/` (manual copy or future automation).
2. Copy `setup-vvoBG.exe` and `vvoBG.tp2` into the BG2EE game directory.
3. Run the WeiDU installer from the game folder.

Refer to `TESTING.md` for verification steps.
