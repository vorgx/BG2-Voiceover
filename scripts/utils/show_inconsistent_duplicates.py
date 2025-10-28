"""
Show examples of inconsistent duplicate StrRef entries.

Displays StrRefs where the same ID has different text or speakers across duplicates.
"""

import csv
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]
ALL_LINES_CSV = ROOT / "data" / "all_lines.csv"


def find_inconsistent_duplicates():
    """Find duplicates with inconsistent data"""
    print("=" * 80)
    print("INCONSISTENT DUPLICATE StrRef ENTRIES")
    print("=" * 80)
    
    print(f"\n[*] Scanning {ALL_LINES_CSV}...")
    
    # Track all occurrences of each StrRef
    strref_occurrences = defaultdict(list)
    
    with open(ALL_LINES_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):
            strref = row['StrRef']
            strref_occurrences[strref].append({
                'row': row_num,
                'Speaker': row['Speaker'],
                'Text': row['Text'],
                'Original_VO_WAV': row.get('Original_VO_WAV', ''),
                'Generated_VO_WAV': row.get('Generated_VO_WAV', ''),
                'DLG_File': row.get('DLG_File', '')
            })
    
    # Find inconsistent duplicates
    inconsistent = []
    for strref, occurrences in strref_occurrences.items():
        if len(occurrences) > 1:
            texts = set(occ['Text'] for occ in occurrences)
            speakers = set(occ['Speaker'] for occ in occurrences)
            if len(texts) > 1 or len(speakers) > 1:
                inconsistent.append((strref, occurrences, texts, speakers))
    
    print(f"[*] Found {len(inconsistent)} StrRefs with inconsistent duplicates")
    
    # Show first 10 examples
    print(f"\n{'='*80}")
    print("EXAMPLES (First 10)")
    print("="*80)
    
    for strref, occurrences, texts, speakers in inconsistent[:10]:
        print(f"\n[StrRef {strref}] - {len(occurrences)} occurrences")
        print(f"  Unique texts: {len(texts)}")
        print(f"  Unique speakers: {len(speakers)}")
        print()
        
        for occ in occurrences:
            text_preview = occ['Text'][:70] + '...' if len(occ['Text']) > 70 else occ['Text']
            print(f"  Row {occ['row']:>6} | Speaker: {occ['Speaker']:<15} | DLG: {occ['DLG_File']:<15}")
            print(f"           Text: {text_preview}")
            if occ['Original_VO_WAV']:
                print(f"           Original: {occ['Original_VO_WAV']}")
            if occ['Generated_VO_WAV']:
                print(f"           Generated: {occ['Generated_VO_WAV']}")


if __name__ == '__main__':
    find_inconsistent_duplicates()
