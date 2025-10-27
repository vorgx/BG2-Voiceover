"""Generate pseudo reference audio clips for speakers.

The script reads short seed prompts from `data/style_seeds/<Speaker>.txt` and
renders them via Index‑TTS to `refs/<Speaker>.wav`. The seeds are meant to be
hand-authored. By default the script performs a dry run to show which clips
would be generated.

Usage examples::

    python scripts/gen_pseudorefs.py --dry-run
    python scripts/gen_pseudorefs.py --speaker Jaheira
    python scripts/gen_pseudorefs.py --all

The actual rendering step reuses the absolute Index‑TTS paths defined in
`scripts/synth.py`, so the tool inherits the existing environment setup.
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Iterable

from scripts.synth import INDEX_TTS_BIN, COMMON_ARGS, sanitize  # type: ignore

ROOT = Path(__file__).resolve().parents[2]
SEEDS_DIR = ROOT / "data" / "style_seeds"
REFS_DIR = ROOT / "refs"
VOICES_JSON = ROOT / "data" / "voices.json"


def iter_seed_files(speakers: Iterable[str] | None = None) -> Iterable[Path]:
    if not SEEDS_DIR.exists():
        return []
    chosen = {name.lower() for name in speakers} if speakers else None
    for path in sorted(SEEDS_DIR.glob("*.txt")):
        if chosen and path.stem.lower() not in chosen:
            continue
        yield path


def render_seed(seed_file: Path, dry_run: bool = True) -> None:
    target = REFS_DIR / f"{seed_file.stem}.wav"
    if target.exists():
        print(f"skip {target.name} (already exists)")
        return

    lines = [sanitize(line.strip()) for line in seed_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        print(f"{seed_file.name}: no non-empty lines, skipping")
        return

    if dry_run:
        print(f"DRY RUN → would render {len(lines)} prompts to {target}")
        return

    REFS_DIR.mkdir(parents=True, exist_ok=True)

    with target.open("wb") as out_file:
        for text in lines:
            temp = target.with_suffix(".tmp.wav")
            args = [INDEX_TTS_BIN, *COMMON_ARGS, "-v", "narrator", "-o", str(temp), text]
            subprocess.run(args, check=True)
            out_file.write(temp.read_bytes())
            temp.unlink(missing_ok=True)
    print(f"wrote {target}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate pseudo reference clips for Index-TTS conditioning.")
    parser.add_argument("--speaker", action="append", help="Limit rendering to specific speakers")
    parser.add_argument("--dry-run", action="store_true", help="Show operations without rendering")
    parser.add_argument("--all", action="store_true", help="Render all speakers with seed files")
    args = parser.parse_args()

    if not SEEDS_DIR.exists():
        print("No style seeds directory found; create data/style_seeds/ to use this tool.")
        return

    speakers = args.speaker if args.speaker else (None if args.all else [])
    files = list(iter_seed_files(speakers))
    if not files:
        print("No matching seed files found.")
        return

    for seed in files:
        render_seed(seed, dry_run=args.dry_run and not args.all)


if __name__ == "__main__":
    main()
