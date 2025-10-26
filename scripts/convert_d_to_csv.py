"""Convert Near Infinity mass-exported .D dialogue files to *_dlg.csv.

The mass exporter writes WeiDU-style .D text files. This script extracts all
StrRef numbers used in SAY/REPLY statements so downstream tooling can join them
with dialog.tlk.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Iterable, Set

ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "BG2 Files" / "Dialog Files"
OUTPUT_DIR = ROOT / "exports" / "ni"

# Regex matches SAY #12345 (ignores whitespace/comments). Replies are skipped.
STRREF_RE = re.compile(r"\bSAY\s+#(?P<id>\d+)\b")


def extract_strrefs(path: Path) -> Set[int]:
    """Return the set of StrRef integers found in a .D file."""
    strrefs: Set[int] = set()

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return strrefs

    for match in STRREF_RE.finditer(text):
        try:
            strrefs.add(int(match.group("id")))
        except ValueError:
            continue

    return strrefs


def write_csv(path: Path, strrefs: Iterable[int]) -> None:
    """Write *_dlg.csv file with StrRef column."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["StrRef"])
        for strref in sorted(set(strrefs)):
            writer.writerow([strref])


def main() -> None:
    if not INPUT_DIR.exists():
        raise SystemExit(f"❌ Input directory not found: {INPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    converted = 0
    total_refs = 0

    for source in sorted(INPUT_DIR.glob("*.D")):
        strrefs = extract_strrefs(source)
        if not strrefs:
            continue

        target = OUTPUT_DIR / f"{source.stem}_dlg.csv"
        write_csv(target, strrefs)

        converted += 1
        total_refs += len(strrefs)

    if converted == 0:
        print(f"⚠️ No dialogue StrRefs found under {INPUT_DIR}")
        return

    print(f"✅ Converted {converted} dialogue files → {OUTPUT_DIR}")
    print(f"   Total StrRefs extracted: {total_refs:,}")


if __name__ == "__main__":
    main()
