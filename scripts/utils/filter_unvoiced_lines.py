"""Filter chapter1_lines.csv to include ONLY lines without existing voice acting.

Reads .D dialog files to identify which StrRefs have [WAVFILE] references.
Creates a new CSV with only unvoiced lines.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[2]
DIALOG_DIR = ROOT / "BG2 Files" / "Dialog Files"
INPUT_CSV = ROOT / "data" / "chapter1_lines.csv"
OUTPUT_CSV = ROOT / "data" / "chapter1_unvoiced.csv"
OUTPUT_WITH_WAV = ROOT / "data" / "chapter1_with_wav_refs.csv"

# Match: SAY #12345 /* ~text~ [WAVFILE] */
VOICED_PATTERN = re.compile(r'\bSAY\s+#(\d+)\s+/\*[^*]*\[([A-Z0-9_]+)\]\s*\*/', re.DOTALL)


def get_voiced_strrefs() -> Dict[int, str]:
    """Return dict mapping StrRef to WAV filename for lines with voice acting."""
    voiced = {}
    
    if not DIALOG_DIR.exists():
        print(f"⚠️ Dialog directory not found: {DIALOG_DIR}")
        return voiced
    
    for d_file in DIALOG_DIR.glob("*.D"):
        try:
            content = d_file.read_text(encoding="utf-8", errors="ignore")
            for match in VOICED_PATTERN.finditer(content):
                strref = int(match.group(1))
                wav_file = match.group(2)
                voiced[strref] = wav_file
        except Exception as e:
            print(f"⚠️ Error reading {d_file.name}: {e}")
            continue
    
    return voiced


def filter_unvoiced_lines() -> None:
    """Filter chapter1_lines.csv to keep only unvoiced lines."""
    
    if not INPUT_CSV.exists():
        print(f"❌ Input file not found: {INPUT_CSV}")
        return
    
    print("🔍 Scanning .D files for voiced lines...")
    voiced_strrefs = get_voiced_strrefs()
    print(f"   Found {len(voiced_strrefs)} lines with existing voice acting")
    
    # Read input CSV
    with INPUT_CSV.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_lines = list(reader)
    
    # Separate unvoiced and voiced lines
    unvoiced_lines = []
    voiced_lines = []
    
    for row in all_lines:
        strref = int(row['StrRef'])
        if strref in voiced_strrefs:
            # Add WAV reference
            row_with_wav = row.copy()
            row_with_wav['Original_VO_WAV'] = voiced_strrefs[strref]
            voiced_lines.append(row_with_wav)
        else:
            row_with_wav = row.copy()
            row_with_wav['Original_VO_WAV'] = ''
            unvoiced_lines.append(row_with_wav)
    
    # Write complete CSV with WAV references
    with OUTPUT_WITH_WAV.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['StrRef', 'Speaker', 'Text', 'Original_VO_WAV'])
        writer.writeheader()
        writer.writerows(unvoiced_lines + voiced_lines)
    
    print(f"\n✅ Created {OUTPUT_WITH_WAV}")
    print(f"   Total lines: {len(all_lines)}")
    print(f"   Lines with WAV references: {len(voiced_lines)}")
    print(f"   Lines without WAV: {len(unvoiced_lines)}")
    
    # Write filtered CSV (unvoiced only)
    if unvoiced_lines:
        with OUTPUT_CSV.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['StrRef', 'Speaker', 'Text'])
            # Remove Original_VO_WAV column for unvoiced CSV
            unvoiced_without_wav = [{k: v for k, v in row.items() if k != 'Original_VO_WAV'} for row in unvoiced_lines]
            writer.writeheader()
            writer.writerows(unvoiced_without_wav)
        
        print(f"\n✅ Created {OUTPUT_CSV}")
        print(f"   Unvoiced lines (to generate): {len(unvoiced_lines)}")
        print(f"   Voiced lines (skipped): {len(voiced_lines)}")
        
        # Show some examples of voiced lines (with WAV refs)
        if voiced_lines:
            print(f"\n📋 Example lines WITH voice acting (WAV references):")
            for row in voiced_lines[:5]:
                text_preview = row['Text'][:50] + "..." if len(row['Text']) > 50 else row['Text']
                print(f"   {row['StrRef']} ({row['Speaker']}) [{row['Original_VO_WAV']}]: {text_preview}")
        
        # Show some examples of unvoiced lines
        if unvoiced_lines:
            print(f"\n📋 Example lines WITHOUT voice acting (need generation):")
            for row in unvoiced_lines[:5]:
                text_preview = row['Text'][:50] + "..." if len(row['Text']) > 50 else row['Text']
                print(f"   {row['StrRef']} ({row['Speaker']}): {text_preview}")
    else:
        print(f"\n⚠️ No unvoiced lines found! All {len(all_lines)} lines already have voice acting.")


if __name__ == "__main__":
    filter_unvoiced_lines()
