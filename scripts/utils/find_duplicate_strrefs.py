"""
Find duplicate StrRef entries in all_lines.csv

Identifies rows where the same StrRef appears multiple times.
This can happen when the same dialogue line is used in multiple dialogue files.
"""

import csv
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]
ALL_LINES_CSV = ROOT / "data" / "all_lines.csv"


def find_duplicates():
    """Find all duplicate StrRef entries"""
    print("=" * 80)
    print("FINDING DUPLICATE StrRef ENTRIES")
    print("=" * 80)
    
    print(f"\n[*] Scanning {ALL_LINES_CSV}...")
    
    # Track all occurrences of each StrRef
    strref_occurrences = defaultdict(list)
    
    with open(ALL_LINES_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            strref = row['StrRef']
            strref_occurrences[strref].append({
                'row': row_num,
                'Speaker': row['Speaker'],
                'Text': row['Text'][:80] + '...' if len(row['Text']) > 80 else row['Text'],
                'Original_VO_WAV': row.get('Original_VO_WAV', ''),
                'Generated_VO_WAV': row.get('Generated_VO_WAV', ''),
                'DLG_File': row.get('DLG_File', '')
            })
    
    # Filter to only duplicates
    duplicates = {k: v for k, v in strref_occurrences.items() if len(v) > 1}
    
    print(f"[*] Total unique StrRefs: {len(strref_occurrences)}")
    print(f"[*] Duplicate StrRefs found: {len(duplicates)}")
    
    if not duplicates:
        print("\n[+] No duplicates found!")
        return
    
    # Sort by number of occurrences (most duplicated first)
    sorted_dups = sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)
    
    print(f"\n{'='*80}")
    print("DUPLICATE ENTRIES")
    print("="*80)
    
    for strref, occurrences in sorted_dups[:20]:  # Show top 20
        print(f"\nStrRef {strref}: {len(occurrences)} occurrences")
        for occ in occurrences:
            original = occ['Original_VO_WAV'][:15] if occ['Original_VO_WAV'] else '(none)'
            generated = occ['Generated_VO_WAV'][:15] if occ['Generated_VO_WAV'] else '(none)'
            print(f"  Row {occ['row']:>6} | {occ['Speaker']:<15} | DLG: {occ['DLG_File']:<15} | Orig: {original:<15} | Gen: {generated:<15}")
            print(f"           Text: {occ['Text']}")
    
    if len(duplicates) > 20:
        print(f"\n... and {len(duplicates) - 20} more duplicate StrRefs")
    
    # Statistics
    print(f"\n{'='*80}")
    print("STATISTICS")
    print("="*80)
    total_duplicate_rows = sum(len(v) - 1 for v in duplicates.values())
    print(f"Total duplicate rows (extras): {total_duplicate_rows}")
    print(f"Rows that would remain if deduplicated: {len(strref_occurrences)}")
    print(f"Rows currently in file: {sum(len(v) for v in strref_occurrences.values())}")
    
    # Check if duplicates have different data
    inconsistent = []
    for strref, occurrences in duplicates.items():
        texts = set(occ['Text'] for occ in occurrences)
        speakers = set(occ['Speaker'] for occ in occurrences)
        if len(texts) > 1 or len(speakers) > 1:
            inconsistent.append(strref)
    
    if inconsistent:
        print(f"\n[!] WARNING: {len(inconsistent)} StrRefs have INCONSISTENT data across duplicates!")
        print("    (Different text or speaker for same StrRef)")
        for strref in inconsistent[:10]:
            print(f"    - StrRef {strref}")
        if len(inconsistent) > 10:
            print(f"    ... and {len(inconsistent) - 10} more")
    else:
        print("\n[+] All duplicates have consistent data (same text/speaker)")


if __name__ == '__main__':
    find_duplicates()
