"""Update characters.csv with all actual DLG files from all_lines.csv"""
import csv
from collections import defaultdict
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
all_lines_csv = ROOT / "data" / "all_lines.csv"
characters_csv = ROOT / "data" / "characters.csv"

print("[*] Analyzing DLG files from all_lines.csv...")

# Load actual DLG files from all_lines.csv
by_speaker = defaultdict(set)
with open(all_lines_csv, 'r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        speaker = row['Speaker'].strip()
        dlg_file = row.get('DLG_File', '').strip()
        if speaker and dlg_file:
            by_speaker[speaker].add(dlg_file)

print(f"   Found {len(by_speaker)} unique speakers")

# Load characters.csv
print("[*] Loading characters.csv...")
characters = []
with open(characters_csv, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        characters.append(row)

print(f"   Found {len(characters)} characters")

# Create backup
backup_path = characters_csv.parent / f"characters_before_dlg_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
print(f"[*] Creating backup: {backup_path.name}")
with open(backup_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(characters)

# Update DLGFiles for each character
print("[*] Updating DLGFiles column...")
updated_count = 0
for row in characters:
    canonical = row['Canonical'].strip()
    
    # Get actual DLG files from data
    actual_dlg = by_speaker.get(canonical, set())
    if not actual_dlg:
        continue
    
    # Get currently listed DLG files
    dlg_files_str = row.get('DLGFiles', '').strip()
    if dlg_files_str:
        listed_dlg = set()
        for dlg in dlg_files_str.split('|'):
            dlg_clean = dlg.strip().upper()
            if dlg_clean.endswith('.DLG'):
                dlg_clean = dlg_clean[:-4]
            listed_dlg.add(dlg_clean)
    else:
        listed_dlg = set()
    
    # Check if update needed
    missing = actual_dlg - listed_dlg
    if missing:
        # Update with all actual DLG files (sorted, with .DLG extension)
        new_dlg_list = '|'.join(f"{dlg}.DLG" for dlg in sorted(actual_dlg))
        row['DLGFiles'] = new_dlg_list
        updated_count += 1
        print(f"   [{canonical:12}] Added {len(missing)} missing files: {' '.join(sorted(missing))}")

# Write updated characters.csv
print(f"[*] Writing updated characters.csv...")
with open(characters_csv, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(characters)

print()
print("="*80)
print(f"[+] Updated {updated_count} characters")
print(f"[+] Backup saved: {backup_path.name}")
print("="*80)
