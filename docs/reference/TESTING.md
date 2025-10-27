# Testing & QA Checklist

This document consolidates verification steps for the BG2 Voiceover project.

## 1. Data Integrity
- **Sanitization**: Run the snippet in `../getting-started/CHAPTER_PIPELINE.md` to ensure no `<TOKEN>` placeholders remain.
- **Speaker counts**: Recompute counts after each chapter refresh and compare against previous totals to spot regressions.

## 2. Script Smoke Tests
- `python scripts/convert_d_to_csv.py` → should finish without errors when `BG2 Files/Dialog Files` contains `.D` files.
- `python scripts/near_infinity_join.py` → should produce `data/lines.csv` with populated text.
- `python scripts/synth.py` → import check succeeds; `if __name__ == "__main__"` guard prevents accidental batch synthesis during import.
- `python scripts/build_cards.py` (stub) → prints guidance/TODO rather than modifying files yet.

## 3. CLI
- `python -m bg2vo env` → prints the paths configured in `config/defaults.yaml`.
- `python -m bg2vo count --chapter 1` → summarizes chapter line counts (matches snippet used earlier).

## 4. Audio QA
- Inspect random samples in `build/OGG/` with a waveform viewer.
- Ensure file format matches 22.05 kHz, 16-bit, mono.
- Cross-check sanitized text vs spoken content for clarity and pacing.

## 5. Staging & Installation
- After staging, run WeiDU in a dry-run game directory to verify installation, then uninstall to keep the dev environment clean.

## 6. Automated Tests (Future)
- Placeholder `tests/test_cache.py` verifies cache persistence once hooks are wired.
- Additional tests can validate CLI behaviours and sanitization routines as the blueprint components mature.
