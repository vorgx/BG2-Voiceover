"""Join Near Infinity exports to produce data/lines.csv."""
from __future__ import annotations

import csv
import os
import struct
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "exports" / "ni"
OUTPUT = ROOT / "data" / "lines.csv"

# Candidate TLK locations. Users can override with BG2_DIALOG_TLK.
DEFAULT_TLK_PATHS = [
    ROOT / "BG2 Files" / "dialog.tlk",
    Path(r"E:/SteamLibrary/steamapps/common/Baldur's Gate II Enhanced Edition/lang/en_US/dialog.tlk"),
    Path(r"C:/Program Files (x86)/Steam/steamapps/common/Baldur's Gate II Enhanced Edition/lang/en_US/dialog.tlk"),
]

# Character DLG file mappings
COMPANIONS = {
    "IMOEN": "Imoen",
    "IMOENJ": "Imoen",
    "MINSC": "Minsc",
    "MINSCJ": "Minsc",
    "JAHEIRA": "Jaheira",
    "JAHEIRAJ": "Jaheira",
    "VICONIA": "Viconia",
    "VVICONI": "Viconia",
    "EDWIN": "Edwin",
    "EDWINJ": "Edwin",
    "AERIE": "Aerie",
    "AERIEJ": "Aerie",
    "KORGAN": "Korgan",
    "KORGANJ": "Korgan",
    "ANOMEN": "Anomen",
    "ANOMENJ": "Anomen",
    "KELDORN": "Keldorn",
    "KELDORJ": "Keldorn",
    "NALIA": "Nalia",
    "NALIAJ": "Nalia",
    "HAERDALI": "HaerDalis",
    "HAERDA": "HaerDalis",
}


def load_tlk_csv(tlk_csv: Path) -> Dict[int, str]:
    """Load StrRef -> text mapping from a CSV export."""
    strref_map: Dict[int, str] = {}

    with tlk_csv.open("r", encoding="utf-8", errors="ignore") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            try:
                strref = int(row["StrRef"])
            except (ValueError, KeyError):
                continue

            text = row.get("Text", "").strip()
            if text:
                strref_map[strref] = text

    return strref_map


def load_tlk_binary(tlk_path: Path) -> Dict[int, str]:
    """Parse a binary dialog.tlk file and return StrRef -> text."""
    data = tlk_path.read_bytes()
    if len(data) < 18:
        raise ValueError(f"TLK file too small: {tlk_path}")

    signature, version, language_id, string_count, string_offset = struct.unpack(
        "<4s4sHII", data[:18]
    )

    if signature != b"TLK " or not version.startswith(b"V1"):
        raise ValueError(f"Unexpected TLK header: {signature!r} {version!r}")

    entries_offset = 18
    entry_size = 26
    entries_end = entries_offset + string_count * entry_size
    if entries_end > len(data):
        raise ValueError("TLK entry table exceeds file length")

    strref_map: Dict[int, str] = {}

    for index in range(string_count):
        start = entries_offset + index * entry_size
        end = start + entry_size
        flags, sound_resref, vol_var, pitch_var, offset, length = struct.unpack(
            "<H8sIIII", data[start:end]
        )

        has_text = bool(flags & 0x0001)
        if not has_text or length == 0:
            continue

        absolute = string_offset + offset
        text_bytes = data[absolute : absolute + length]
        text = text_bytes.decode("cp1252", errors="ignore").strip()

        if text:
            strref_map[index] = text

    return strref_map


def find_tlk_source() -> Tuple[str, Path]:
    """Locate TLK data from CSV export or a binary dialog.tlk."""
    csv_path = EXPORTS / "dialog_tlk.csv"
    if csv_path.exists():
        return ("csv", csv_path)

    env_path = os.environ.get("BG2_DIALOG_TLK")
    candidates = []
    if env_path:
        candidates.append(Path(env_path))
    candidates.extend(DEFAULT_TLK_PATHS)

    for candidate in candidates:
        if candidate.exists():
            return ("binary", candidate)

    raise FileNotFoundError(
        "No TLK source found. Export dialog.tlk to exports/ni/dialog_tlk.csv "
        "or set BG2_DIALOG_TLK to the game's dialog.tlk path."
    )


def load_dlg_files(exports_dir: Path) -> Dict[int, str]:
    """Load all exported *_dlg.csv files and map StrRef -> speaker."""
    strref_speakers: Dict[int, str] = {}

    for dlg_file in exports_dir.glob("*_dlg.csv"):
        dlg_stem = dlg_file.stem.replace("_dlg", "").upper()
        speaker = COMPANIONS.get(dlg_stem, dlg_stem.title())

        with dlg_file.open("r", encoding="utf-8", errors="ignore") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                try:
                    strref = int(row.get("StrRef", -1))
                except (ValueError, TypeError):
                    continue

                if strref <= 0:
                    continue

                if strref not in strref_speakers:
                    strref_speakers[strref] = speaker

    return strref_speakers


def main() -> None:
    print("=" * 60)
    print("Near Infinity Bulk Join")
    print("=" * 60)

    try:
        tlk_kind, tlk_path = find_tlk_source()
    except FileNotFoundError as exc:
        print(f"❌ {exc}")
        return

    if tlk_kind == "csv":
        print(f"\n📁 Loading TLK CSV: {tlk_path}")
        strref_text = load_tlk_csv(tlk_path)
    else:
        print(f"\n📁 Loading TLK binary: {tlk_path}")
        strref_text = load_tlk_binary(tlk_path)

    print(f"   ✓ Loaded {len(strref_text):,} text entries")

    print(f"\n📁 Loading DLG exports from: {EXPORTS}")
    dlg_files = list(EXPORTS.glob("*_dlg.csv"))
    if not dlg_files:
        print("❌ Error: No *_dlg.csv files found in exports/ni")
        print("   Run scripts/convert_d_to_csv.py after the mass export.")
        return

    print(f"   Found {len(dlg_files)} DLG files")
    strref_speakers = load_dlg_files(EXPORTS)
    print(f"   ✓ Mapped {len(strref_speakers):,} StrRefs to speakers")

    print(f"\n📝 Creating {OUTPUT}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    lines_written = 0
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["StrRef", "Speaker", "Text"])

        for strref, speaker in sorted(strref_speakers.items()):
            text = strref_text.get(strref)
            if not text:
                continue

            writer.writerow([strref, speaker, text])
            lines_written += 1

    print(f"   ✓ Wrote {lines_written:,} joined lines")

    speaker_counts = defaultdict(int)
    for speaker in strref_speakers.values():
        speaker_counts[speaker] += 1

    print("\n📊 Lines per speaker:")
    for speaker, count in sorted(speaker_counts.items(), key=lambda item: -item[1]):
        print(f"   {speaker:15s}: {count:4,} lines")

    print(f"\n✅ Done! Output saved to {OUTPUT}")
    print("=" * 60)


if __name__ == "__main__":
    main()
