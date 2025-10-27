"""Monitor synthesis progress without interrupting the process.

Usage:
    python scripts/check_progress.py --input data/test_lines.csv
    python scripts/check_progress.py --chapter 1
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from bg2vo.config import load_config  # type: ignore[import-not-found]

try:
    settings = load_config()
    OUT = Path(settings.outputs.get("ogg_dir", "build/OGG"))
    if not OUT.is_absolute():
        OUT = ROOT / OUT
except Exception:
    OUT = ROOT / "build" / "OGG"


def check_progress(input_csv: Path) -> None:
    """Check how many lines have been synthesized."""
    if not input_csv.exists():
        print(f"❌ Input CSV not found: {input_csv}")
        return

    expected_refs = []
    with input_csv.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            expected_refs.append(row["StrRef"])

    total = len(expected_refs)
    completed = []
    missing = []

    for strref in expected_refs:
        wav_path = OUT / f"{strref}.wav"
        if wav_path.exists():
            size_kb = wav_path.stat().st_size / 1024
            completed.append((strref, size_kb))
        else:
            missing.append(strref)

    # Display results
    print(f"\n{'='*60}")
    print(f"Synthesis Progress: {input_csv.name}")
    print(f"{'='*60}")
    print(f"\n✅ Completed: {len(completed)}/{total} ({len(completed)/total*100:.1f}%)")
    print(f"⏳ Remaining: {len(missing)}/{total}")
    
    if completed:
        print(f"\n📊 Generated files:")
        for strref, size in completed[-5:]:  # Show last 5
            print(f"   {strref}.wav ({size:.1f} KB)")
    
    if missing:
        print(f"\n⏳ Next up: {missing[:5]}")  # Show next 5
    
    print(f"\n📁 Output directory: {OUT}")
    print(f"{'='*60}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check synthesis progress")
    parser.add_argument("--input", type=Path, help="Input CSV file")
    parser.add_argument("--chapter", type=int, help="Chapter number")
    args = parser.parse_args()

    if args.chapter:
        input_path = ROOT / "data" / f"chapter{args.chapter}_lines.csv"
    elif args.input:
        input_path = args.input
    else:
        input_path = ROOT / "data" / "lines.csv"

    check_progress(input_path)


if __name__ == "__main__":
    main()
