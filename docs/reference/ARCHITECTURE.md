# BG2 Voiceover Architecture

This document summarizes how the repository pieces fit together after integrating the end-to-end blueprint.

## High-Level Flow

1. **Export** dialogue assets from BG2EE using Near Infinity.
2. **Extract** StrRefs from `.D` files (`scripts/convert_d_to_csv.py`).
3. **Join** StrRefs with TLK text to build the canonical `data/lines.csv` (`scripts/near_infinity_join.py`).
4. **Sanitize** lines to remove WeiDU placeholders (`scripts/synth.py` or helper snippets).
5. **Slice** per chapter (`data/chapter*_lines.csv`, `data/chapter*_split/`).
6. **Assign** voices in `data/voices.json` or blueprint `config/voices.sample.json` for staging.
7. **Synthesize** audio via Index‑TTS (`scripts/synth.py` or `bg2vo` CLI).
8. **Stage & Install** with WeiDU (`mod/vvoBG.tp2`, `setup-vvoBG.exe`).

## Repository Layout (Updated)

```
BG2 Voiceover/
├─ config/                   # Blueprint configuration defaults
│  ├─ defaults.yaml
│  └─ voices.sample.json
├─ data/                     # Canonical datasets (sanitized lines)
│  ├─ lines.csv
│  ├─ chapter1_lines.csv
│  └─ chapter1_split/
├─ docs/                     # Process & reference docs (see Index below)
├─ scripts/                  # Automation scripts & helpers (legacy + new stubs)
│  ├─ convert_d_to_csv.py
│  ├─ near_infinity_join.py
│  ├─ synth.py
│  ├─ build_cards.py         # blueprint stub – draft character cards
│  ├─ build_refs.py          # blueprint stub – apply preset rules
│  ├─ gen_pseudorefs.py      # blueprint stub – synth style reference clips
│  └─ synth_cache.py         # cache helper to skip unchanged lines
├─ src/bg2vo/                # future CLI/automation package scaffolding
├─ tests/                    # placeholder for automated tests
├─ tools/                    # helper scripts (installers, env setup)
├─ .github/workflows/        # CI entry point (lint/tests)
├─ mod/                      # WeiDU assets
└─ build/OGG/                # Synthesized output
```

## Data Contracts

- **`data/lines.csv`**: master list of sanitized StrRefs.
- **`data/chapter*_lines.csv`**: chapter-filtered subsets, sanitized.
- **`data/voices.json`**: production mapping (legacy).
- **`config/voices.sample.json`**: blueprint mapping; can be used to seed `data/voices.json`.
- **`config/defaults.yaml`**: centralized location for environment paths.

## Automation Surfaces

- **Legacy scripts**: remain untouched; continue to power Chapter 1 pipeline.
- **Blueprint scripts**: currently stubs with docstrings and TODO markers. They can evolve into the full automation described in the starter kit without disrupting legacy flows.
- **`bg2vo` package**: thin wrappers and helpers referencing existing data until fully implemented.

## Future Enhancements

- Flesh out blueprint stubs (`scripts/build_cards.py`, etc.) to perform real work once the team is ready.
- Transition from ad-hoc scripts to the `bg2vo` CLI gradually while keeping existing scripts usable.
- Expand `tests/` to cover sanitization, voice selection, and staging.

Refer to `USAGE.md` and `PRESETS.md` for operational details.
