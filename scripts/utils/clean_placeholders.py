"""Clean placeholder tokens from all dialogue CSV files.

Applies the same sanitize() logic used in synth.py to clean:
- all_lines.csv
- chapter1_lines.csv through chapter7_lines.csv  
- chapter_unassigned.csv

Replaces tokens like <CHARNAME>, <MANWOMAN>, etc. with readable text.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"

TOKEN_REPLACEMENTS = {
    "CHARNAME": "you",
    "PRO_HESHE": "they",
    "PRO_HIMHER": "them",
    "PRO_HISHER": "their",
    "PRO_MANWOMAN": "person",
    "PRO_LADYLORD": "my friend",
    "LADYLORD": "friend",
    "PRO_RACE": "traveler",
    "RACE": "traveler",
    "PRO_SIRMAAM": "friend",
    "SIRMAAM": "friend",
    "MALEFEMALE": "person",
    "PRO_MALEFEMALE": "person",
    "MANWOMAN": "person",
    "PRO_BROTHERSISTER": "friend",
    "BROTHERSISTER": "friend",
    "PRO_GIRLBOY": "child",
    "GIRLBOY": "child",
    "GABBER": "friend",
    "DAYNIGHTALL": "day",
}

TOKEN_PATTERN = re.compile(r"<([^>]+)>")


def sanitize(text: str) -> str:
    """Normalize dialogue text by removing WeiDU tokens and tidying spacing."""

    def _replace(match: re.Match[str]) -> str:
        token = match.group(1)
        if token == "CHARNAME":
            return "__CHARNAME__"
        return TOKEN_REPLACEMENTS.get(token, "")

    cleaned = TOKEN_PATTERN.sub(_replace, text)
    cleaned = cleaned.replace("~", "")
    cleaned = cleaned.replace("\u00a0", " ")
    fallback = cleaned.replace("__CHARNAME__", "you").strip()
    # Normalize stray mojibake dashes that appear in exports
    cleaned = cleaned.replace("\u2014", "-").replace("\u2013", "-")

    # Remove direct-address placeholders before replacing final token
    cleaned = re.sub(r"(^|[.!?]\s*)__CHARNAME__,\s*", r"\1", cleaned)
    cleaned = re.sub(r"(^|[.!?]\s*)__CHARNAME__\s*[!?]+\s*", r"\1", cleaned)
    cleaned = re.sub(r",\s*__CHARNAME__\s*,", ", ", cleaned)
    cleaned = re.sub(r",\s*__CHARNAME__([.!?])", r"\1", cleaned)
    cleaned = re.sub(r",\s*__CHARNAME__", "", cleaned)

    cleaned = cleaned.replace("__CHARNAME__", "you")
    cleaned = re.sub(r"^(?:[Yy]ou[!?]+\s+)+", "", cleaned)
    cleaned = re.sub(r"^[\s\-—]*[,.;:!?]+\s*", "", cleaned)
    cleaned = cleaned.lstrip('\"')
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"\s+([,.!?;:])", r"\1", cleaned)
    cleaned = re.sub(r",\s*,", ", ", cleaned)
    cleaned = re.sub(r"(?<!\.)\.\.(?!\.)", ".", cleaned)
    cleaned = re.sub(r"([!?;:]){2,}", lambda m: m.group(0)[0], cleaned)
    cleaned = re.sub(r",([!?;:])", r"\1", cleaned)

    return cleaned.strip() if cleaned else fallback


def clean_csv_file(file_path: Path) -> tuple[int, int]:
    """Clean placeholders in a CSV file. Returns (total_lines, cleaned_lines)."""
    
    if not file_path.exists():
        return (0, 0)
    
    # Read file
    with file_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    
    if not rows:
        return (0, 0)
    
    # Clean text column
    cleaned_count = 0
    for row in rows:
        original_text = row.get('Text', '')
        cleaned_text = sanitize(original_text)
        
        if cleaned_text != original_text:
            row['Text'] = cleaned_text
            cleaned_count += 1
    
    # Write back
    with file_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    return (len(rows), cleaned_count)


def main():
    """Clean all CSV files in data directory."""
    
    print("🧹 Cleaning placeholders from CSV files...\n")
    
    files_to_clean = [
        "all_lines.csv",
        "chapter1_lines.csv",
        "chapter2_lines.csv",
        "chapter3_lines.csv",
        "chapter4_lines.csv",
        "chapter5_lines.csv",
        "chapter6_lines.csv",
        "chapter7_lines.csv",
        "chapter_unassigned.csv",
    ]
    
    total_files = 0
    total_lines = 0
    total_cleaned = 0
    
    for filename in files_to_clean:
        file_path = DATA_DIR / filename
        lines, cleaned = clean_csv_file(file_path)
        
        if lines > 0:
            total_files += 1
            total_lines += lines
            total_cleaned += cleaned
            
            percentage = (cleaned / lines * 100) if lines > 0 else 0
            print(f"✅ {filename}")
            print(f"   Lines: {lines}, Cleaned: {cleaned} ({percentage:.1f}%)")
    
    print(f"\n📊 Summary:")
    print(f"   Files processed: {total_files}")
    print(f"   Total lines: {total_lines}")
    print(f"   Lines with placeholders cleaned: {total_cleaned}")
    
    if total_cleaned > 0:
        print(f"\n✨ All files have been cleaned!")
        print(f"   Placeholders like <CHARNAME>, <MANWOMAN>, etc. replaced with readable text.")
    else:
        print(f"\n✨ No placeholders found - files were already clean!")


if __name__ == "__main__":
    main()
