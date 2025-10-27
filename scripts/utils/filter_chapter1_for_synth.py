"""Filter chapter1_lines.csv to only unvoiced lines for synthesis."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT_CSV = ROOT / "data" / "chapter1_lines.csv"
OUTPUT_CSV = ROOT / "data" / "chapter1_unvoiced_only.csv"
BUILD_OGG = ROOT / "build" / "OGG"

# Read all lines
with INPUT_CSV.open('r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    all_lines = list(reader)

# Filter out lines that already have generated WAVs or original game references
unvoiced_lines = []
for line in all_lines:
    strref = line['StrRef']
    has_original = line.get('WAV_Reference', '').strip()
    has_generated = (BUILD_OGG / f"{strref}.wav").exists()
    
    if not has_original and not has_generated:
        unvoiced_lines.append(line)

# Write unvoiced only (keep only StrRef, Speaker, Text for synth.py)
with OUTPUT_CSV.open('w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['StrRef', 'Speaker', 'Text'])
    writer.writeheader()
    for line in unvoiced_lines:
        writer.writerow({
            'StrRef': line['StrRef'],
            'Speaker': line['Speaker'],
            'Text': line['Text']
        })

print(f"✅ Created {OUTPUT_CSV}")
print(f"   Unvoiced lines to generate: {len(unvoiced_lines)}")
print(f"   Voiced lines skipped: {len(all_lines) - len(unvoiced_lines)}")
