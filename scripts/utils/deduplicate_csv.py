"""
Deduplicate all_lines.csv

Removes TRUE duplicate rows where StrRef + Speaker + DLG_File are identical.
Keeps the first occurrence and removes subsequent duplicates.

Note: Different speakers using the same StrRef is VALID in BG2 and should be kept.
Only removes exact duplicate rows.
"""

import csv
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
ALL_LINES_CSV = ROOT / "data" / "all_lines.csv"
BACKUP_CSV = ROOT / "data" / f"all_lines_before_dedup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"


def find_true_duplicates():
    """Find TRUE duplicates: same StrRef + Speaker + DLG_File"""
    print("=" * 80)
    print("FINDING TRUE DUPLICATE ROWS")
    print("=" * 80)
    
    print(f"\n[*] Scanning {ALL_LINES_CSV}...")
    
    rows = []
    seen_keys = {}
    duplicates = []
    
    with open(ALL_LINES_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        for row_num, row in enumerate(reader, start=2):
            # Create unique key: StrRef + Speaker + DLG_File
            key = (row['StrRef'], row['Speaker'], row.get('DLG_File', ''))
            
            if key in seen_keys:
                # This is a duplicate
                duplicates.append({
                    'row_num': row_num,
                    'first_row': seen_keys[key],
                    'StrRef': row['StrRef'],
                    'Speaker': row['Speaker'],
                    'DLG_File': row.get('DLG_File', ''),
                    'Text': row['Text'][:60] + '...' if len(row['Text']) > 60 else row['Text']
                })
            else:
                # First occurrence - remember it and keep it
                seen_keys[key] = row_num
                rows.append(row)
    
    print(f"[*] Total rows read: {len(rows) + len(duplicates)}")
    print(f"[*] Unique rows: {len(rows)}")
    print(f"[*] Duplicate rows to remove: {len(duplicates)}")
    
    return rows, duplicates, fieldnames


def show_duplicate_examples(duplicates):
    """Show examples of duplicates"""
    if not duplicates:
        print("\n[+] No TRUE duplicates found!")
        return
    
    print(f"\n{'='*80}")
    print("DUPLICATE EXAMPLES (first 20)")
    print("="*80)
    
    for dup in duplicates[:20]:
        print(f"\nRow {dup['row_num']} is duplicate of Row {dup['first_row']}")
        print(f"  StrRef: {dup['StrRef']}, Speaker: {dup['Speaker']}, DLG: {dup['DLG_File']}")
        print(f"  Text: {dup['Text']}")
    
    if len(duplicates) > 20:
        print(f"\n... and {len(duplicates) - 20} more duplicates")


def save_deduplicated(rows, fieldnames):
    """Save deduplicated CSV"""
    # Create backup
    print(f"\n[*] Creating backup: {BACKUP_CSV.name}")
    shutil.copy2(ALL_LINES_CSV, BACKUP_CSV)
    
    # Write deduplicated CSV
    print(f"[*] Writing deduplicated CSV...")
    with open(ALL_LINES_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"[+] Saved {len(rows)} unique rows")


def main():
    """Main deduplication process"""
    
    # Find duplicates
    rows, duplicates, fieldnames = find_true_duplicates()
    
    # Show examples
    show_duplicate_examples(duplicates)
    
    if not duplicates:
        return
    
    # Confirm
    print(f"\n{'='*80}")
    response = input(f"\nRemove {len(duplicates)} duplicate rows? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("[Cancelled] No changes made.")
        return
    
    # Save deduplicated CSV
    save_deduplicated(rows, fieldnames)
    
    # Summary
    print(f"\n{'='*80}")
    print("DEDUPLICATION SUMMARY")
    print("="*80)
    print(f"Original rows:     {len(rows) + len(duplicates)}")
    print(f"Removed duplicates: {len(duplicates)}")
    print(f"Remaining rows:    {len(rows)}")
    print(f"Backup saved:      {BACKUP_CSV}")
    print("\n[+] Deduplication complete!")


if __name__ == '__main__':
    main()
