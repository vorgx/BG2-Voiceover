"""Analyze which DLG files each character actually uses in all_lines.csv"""
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
all_lines_csv = ROOT / "data" / "all_lines.csv"
characters_csv = ROOT / "data" / "characters.csv"

# Load actual DLG files from all_lines.csv
by_speaker = defaultdict(set)
with open(all_lines_csv, 'r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        speaker = row['Speaker'].strip()
        dlg_file = row.get('DLG_File', '').strip()
        if speaker and dlg_file:
            by_speaker[speaker].add(dlg_file)

# Load characters.csv to compare
characters = {}
with open(characters_csv, 'r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        canonical = row['Canonical'].strip()
        dlg_files_str = row.get('DLGFiles', '').strip()
        if dlg_files_str:
            # Split by pipe and clean
            dlg_files = set()
            for dlg in dlg_files_str.split('|'):
                dlg_clean = dlg.strip().upper()
                # Remove .DLG extension for comparison
                if dlg_clean.endswith('.DLG'):
                    dlg_clean = dlg_clean[:-4]
                dlg_files.add(dlg_clean)
            characters[canonical] = dlg_files

print("="*80)
print("Character DLG File Analysis")
print("="*80)
print()

# Main party characters to check
main_chars = ['Imoen', 'Minsc', 'Jaheira', 'Aerie', 'Anomen', 'Edwin', 'Viconia', 
              'Korgan', 'Keldorn', 'Nalia', 'HaerDalis', 'Cernd', 'Mazzy', 'Valygar', 
              'Yoshimo', 'Sarevok']

for char in main_chars:
    actual_dlg = by_speaker.get(char, set())
    listed_dlg = characters.get(char, set())
    
    if not actual_dlg:
        continue
    
    missing = actual_dlg - listed_dlg
    
    print(f"{char}:")
    print(f"  Listed in characters.csv ({len(listed_dlg)}): {' | '.join(sorted(listed_dlg))}")
    print(f"  Actually used in data ({len(actual_dlg)}): {' | '.join(sorted(actual_dlg))}")
    
    if missing:
        print(f"  [!] MISSING ({len(missing)}): {' | '.join(sorted(missing))}")
    else:
        print(f"  [+] Complete!")
    print()

# Show summary
total_missing = sum(1 for char in main_chars if (by_speaker.get(char, set()) - characters.get(char, set())))
print("="*80)
print(f"Summary: {total_missing}/{len([c for c in main_chars if c in by_speaker])} characters have missing DLG files")
print("="*80)
