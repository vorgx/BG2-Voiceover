"""
Cleanup duplicate audio files.

This script identifies lines in all_lines.csv that have BOTH Original_VO_WAV 
(professional voice acting from the original game) and Generated_VO_WAV 
(synthesized audio). It moves the unnecessary synthesized files to an archive 
folder and clears the Generated_VO_WAV column for those lines.

The original voice acting should always be preferred over synthesized audio.
"""

import csv
import shutil
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
ALL_LINES_CSV = PROJECT_ROOT / "data" / "all_lines.csv"
SYNTH_AUDIO_DIR = PROJECT_ROOT / "build" / "OGG"
ARCHIVE_DIR = PROJECT_ROOT / "archive" / "duplicate_synth_audio"
BACKUP_CSV = PROJECT_ROOT / "data" / "all_lines_before_cleanup.csv"

def find_duplicates():
    """Find all lines with both original and generated audio."""
    duplicates = []
    
    with open(ALL_LINES_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            original = row.get('Original_VO_WAV', '').strip()
            generated = row.get('Generated_VO_WAV', '').strip()
            
            # If both are populated, this is a duplicate
            if original and generated:
                duplicates.append({
                    'StrRef': row['StrRef'],
                    'Speaker': row['Speaker'],
                    'Original_VO_WAV': original,
                    'Generated_VO_WAV': generated,
                    'Chapter': row.get('Chapter', ''),
                    'DLG_File': row.get('DLG_File', '')
                })
    
    return duplicates

def move_to_archive(duplicates):
    """Move duplicate synthesized files to archive folder."""
    # Create archive directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_subdir = ARCHIVE_DIR / timestamp
    archive_subdir.mkdir(parents=True, exist_ok=True)
    
    moved_count = 0
    missing_count = 0
    total_size = 0
    
    print(f"\n[Archive] Moving files to: {archive_subdir}")
    
    for dup in duplicates:
        synth_file = SYNTH_AUDIO_DIR / dup['Generated_VO_WAV']
        
        if synth_file.exists():
            # Get file size before moving
            file_size = synth_file.stat().st_size
            total_size += file_size
            
            # Move to archive
            dest_file = archive_subdir / dup['Generated_VO_WAV']
            shutil.move(str(synth_file), str(dest_file))
            moved_count += 1
            
            if moved_count <= 5:  # Show first 5 examples
                print(f"  [+] Moved {dup['Generated_VO_WAV']} (StrRef {dup['StrRef']}, {dup['Speaker']})")
        else:
            missing_count += 1
            if missing_count <= 5:
                print(f"  [!] File not found: {dup['Generated_VO_WAV']} (StrRef {dup['StrRef']})")
    
    if moved_count > 5:
        print(f"  ... and {moved_count - 5} more files")
    
    return moved_count, missing_count, total_size, archive_subdir

def update_csv(duplicates):
    """Clear Generated_VO_WAV column for duplicate entries."""
    # Create set of StrRefs to clear
    strrefs_to_clear = {dup['StrRef'] for dup in duplicates}
    
    # Read all rows
    rows = []
    with open(ALL_LINES_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        for row in reader:
            if row['StrRef'] in strrefs_to_clear:
                # Clear Generated_VO_WAV for this row
                row['Generated_VO_WAV'] = ''
            rows.append(row)
    
    # Create backup
    print(f"\n[Backup] Creating backup: {BACKUP_CSV}")
    shutil.copy2(ALL_LINES_CSV, BACKUP_CSV)
    
    # Write updated CSV
    with open(ALL_LINES_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"[Update] Cleared Generated_VO_WAV for {len(strrefs_to_clear)} rows")

def create_archive_manifest(archive_dir, duplicates, moved_count, missing_count, total_size):
    """Create a manifest file in the archive directory."""
    manifest_path = archive_dir / "MANIFEST.txt"
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(f"Duplicate Audio Archive - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total files archived: {moved_count}\n")
        f.write(f"Missing files (already deleted): {missing_count}\n")
        f.write(f"Total size: {total_size / (1024*1024):.2f} MB\n\n")
        f.write("These files were synthesized unnecessarily because the lines already had\n")
        f.write("professional voice acting from the original game (Original_VO_WAV).\n\n")
        f.write("=" * 80 + "\n\n")
        f.write("Files archived:\n\n")
        
        for dup in sorted(duplicates, key=lambda x: int(x['StrRef'])):
            f.write(f"StrRef {dup['StrRef']:>6} | {dup['Speaker']:<15} | ")
            f.write(f"Original: {dup['Original_VO_WAV']:<15} | ")
            f.write(f"Generated: {dup['Generated_VO_WAV']}\n")
    
    print(f"[Manifest] Created: {manifest_path}")

def main():
    """Main cleanup process."""
    print("=" * 80)
    print("Cleanup Duplicate Audio Files")
    print("=" * 80)
    
    # Find duplicates
    print("\n[Scan] Searching for duplicate audio entries...")
    duplicates = find_duplicates()
    print(f"[Found] {len(duplicates)} lines with both original and generated audio")
    
    if not duplicates:
        print("\n[Done] No duplicates found. Nothing to clean up.")
        return
    
    # Show some examples
    print("\n[Examples] First 5 duplicates:")
    for dup in duplicates[:5]:
        print(f"  StrRef {dup['StrRef']:>6} | {dup['Speaker']:<15} | "
              f"Original: {dup['Original_VO_WAV']:<15} | "
              f"Generated: {dup['Generated_VO_WAV']}")
    
    if len(duplicates) > 5:
        print(f"  ... and {len(duplicates) - 5} more")
    
    # Confirm
    response = input(f"\n[Confirm] Move {len(duplicates)} synthesized files to archive? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("[Cancelled] No changes made.")
        return
    
    # Move files to archive
    moved_count, missing_count, total_size, archive_dir = move_to_archive(duplicates)
    
    # Update CSV
    update_csv(duplicates)
    
    # Create manifest
    create_archive_manifest(archive_dir, duplicates, moved_count, missing_count, total_size)
    
    # Summary
    print("\n" + "=" * 80)
    print("CLEANUP SUMMARY")
    print("=" * 80)
    print(f"Files moved to archive:    {moved_count}")
    print(f"Files missing (skipped):   {missing_count}")
    print(f"Total size archived:       {total_size / (1024*1024):.2f} MB")
    print(f"CSV rows updated:          {len(duplicates)}")
    print(f"Archive location:          {archive_dir}")
    print(f"CSV backup created:        {BACKUP_CSV}")
    print("\n[Done] Cleanup complete!")
    print("\nThe original voice acting (Original_VO_WAV) will be used for these lines.")
    print("Archived files can be restored if needed.")

if __name__ == '__main__':
    main()
