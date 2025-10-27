"""
Split chapter1_lines.csv into separate files per speaker.
"""
import csv
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data" / "chapter1_lines.csv"
OUTPUT_DIR = ROOT / "data" / "chapter1_split"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Read all lines
with open(INPUT, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    lines_by_speaker = defaultdict(list)
    
    for row in reader:
        speaker = row['Speaker']
        lines_by_speaker[speaker].append({
            'StrRef': row['StrRef'],
            'Text': row['Text']
        })

# Write separate files
for speaker, lines in lines_by_speaker.items():
    output_file = OUTPUT_DIR / f"{speaker.lower()}_lines.csv"
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['StrRef', 'Text'])
        writer.writeheader()
        writer.writerows(lines)
    
    print(f"✓ {speaker:15} -> {output_file.name:25} ({len(lines):3} lines)")

print(f"\n✅ Split {sum(len(l) for l in lines_by_speaker.values())} lines into {len(lines_by_speaker)} files")
