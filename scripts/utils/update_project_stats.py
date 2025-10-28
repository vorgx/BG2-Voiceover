"""
Update Project Statistics

This script automatically updates character statistics in characters.csv:
- Total_Lines: Total dialogue lines for this character in all_lines.csv
- VO_Lines: Number of lines synthesized (exist in build/OGG/)
- No_VO_Yet: Lines remaining to synthesize (Total_Lines - VO_Lines)

Usage:
    python scripts/utils/update_project_stats.py [--dry-run]
    
Options:
    --dry-run    Show what would be updated without modifying files
"""

import argparse
import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime


def load_all_lines(csv_path: Path) -> dict[str, set[int]]:
    """
    Load all_lines.csv and group StrRefs by character.
    
    Returns:
        Dict mapping canonical character name to set of StrRefs
    """
    print(f"[*] Loading {csv_path}")
    
    lines_by_speaker = defaultdict(set)
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            speaker = row['Speaker']
            strref = int(row['StrRef'])
            
            # Skip empty speakers
            if not speaker:
                continue
            
            lines_by_speaker[speaker].add(strref)
    
    print(f"   Found {len(lines_by_speaker)} unique speakers")
    return lines_by_speaker


def load_characters(csv_path: Path) -> list[dict]:
    """Load characters.csv"""
    print(f"📖 Loading {csv_path}")
    
    characters = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            characters.append(row)
    
    print(f"   Found {len(characters)} characters")
    return characters


def get_dlg_files(character: dict) -> set[str]:
    """Extract DLG file codes from character's DLGFiles column"""
    dlg_files_str = character.get('DLGFiles', '')
    if not dlg_files_str:
        return set()
    
    # Split by | and remove .DLG extension
    dlg_files = set()
    for dlg in dlg_files_str.split('|'):
        dlg = dlg.strip().replace('.DLG', '')
        if dlg:
            dlg_files.add(dlg)
    
    return dlg_files


def map_speakers_to_characters(characters: list[dict], lines_by_speaker: dict) -> dict:
    """
    Map speakers from all_lines.csv to canonical character names.
    
    Uses DLGFiles column to identify which speakers belong to each character.
    """
    print(f"\n🔗 Mapping speakers to characters...")
    
    speaker_to_character = {}
    
    for char in characters:
        canonical = char['Canonical']
        dlg_files = get_dlg_files(char)
        aliases_str = char.get('Aliases', '')
        aliases = {a.strip() for a in aliases_str.split(';') if a.strip()}
        
        # Match speakers to this character
        for speaker in lines_by_speaker.keys():
            # Direct match with canonical name or aliases
            if speaker == canonical or speaker in aliases:
                speaker_to_character[speaker] = canonical
                continue
            
            # Match with DLG files
            for dlg in dlg_files:
                if speaker.upper().startswith(dlg.upper()):
                    speaker_to_character[speaker] = canonical
                    break
    
    print(f"   Mapped {len(speaker_to_character)} speakers to characters")
    return speaker_to_character


def count_synthesized_files(build_dir: Path) -> set[int]:
    """Count synthesized WAV files in build/OGG/"""
    print(f"\n📊 Counting synthesized files in {build_dir}")
    
    if not build_dir.exists():
        print(f"   [!] Directory not found")
        return set()
    
    synthesized = set()
    for wav_file in build_dir.glob("*.wav"):
        try:
            # Extract StrRef from filename (e.g., "12345.wav" -> 12345)
            strref = int(wav_file.stem.replace('_old', ''))
            synthesized.add(strref)
        except ValueError:
            # Skip non-numeric filenames
            continue
    
    print(f"   Found {len(synthesized)} synthesized files")
    return synthesized


def calculate_character_stats(
    characters: list[dict],
    lines_by_speaker: dict,
    speaker_to_character: dict,
    synthesized: set[int]
) -> list[dict]:
    """Calculate Total_Lines, VO_Lines, No_VO_Yet for each character"""
    print(f"\n📈 Calculating character statistics...")
    
    # Group lines by character
    lines_by_character = defaultdict(set)
    for speaker, char_name in speaker_to_character.items():
        lines_by_character[char_name].update(lines_by_speaker[speaker])
    
    # Update character stats
    updated_characters = []
    for char in characters:
        canonical = char['Canonical']
        all_lines = lines_by_character.get(canonical, set())
        
        total = len(all_lines)
        vo_lines = len(all_lines & synthesized)
        no_vo_yet = total - vo_lines
        
        # Update character dict
        char['Total_Lines'] = str(total)
        char['VO_Lines'] = str(vo_lines)
        char['No_VO_Yet'] = str(no_vo_yet)
        
        updated_characters.append(char)
        
        if total > 0:
            percent = (vo_lines / total * 100) if total > 0 else 0
            print(f"   {canonical:20s}: {total:5d} total, {vo_lines:5d} done ({percent:5.1f}%), {no_vo_yet:5d} remaining")
    
    return updated_characters


def save_characters(csv_path: Path, characters: list[dict], dry_run: bool = False):
    """Save updated characters.csv"""
    if dry_run:
        print(f"\n[?] DRY RUN: Would update {csv_path}")
        return
    
    print(f"\n💾 Saving updated statistics to {csv_path}")
    
    # Ensure all rows have the new columns
    fieldnames = list(characters[0].keys())
    
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(characters)
    
    print(f"   [+] Updated {len(characters)} characters")


def generate_summary_report(characters: list[dict]):
    """Print summary statistics"""
    print(f"\n{'='*70}")
    print(f"PROJECT STATISTICS SUMMARY")
    print(f"{'='*70}\n")
    
    total_lines = sum(int(c['Total_Lines']) for c in characters)
    total_vo = sum(int(c['VO_Lines']) for c in characters)
    total_remaining = sum(int(c['No_VO_Yet']) for c in characters)
    
    overall_percent = (total_vo / total_lines * 100) if total_lines > 0 else 0
    
    print(f"Overall Progress:")
    print(f"  Total Lines:      {total_lines:6d}")
    print(f"  Synthesized:      {total_vo:6d} ({overall_percent:5.1f}%)")
    print(f"  Remaining:        {total_remaining:6d}")
    print(f"\nTop 10 Characters by Lines:")
    
    sorted_chars = sorted(characters, key=lambda c: int(c['Total_Lines']), reverse=True)[:10]
    for i, char in enumerate(sorted_chars, 1):
        total = int(char['Total_Lines'])
        vo = int(char['VO_Lines'])
        percent = (vo / total * 100) if total > 0 else 0
        print(f"  {i:2d}. {char['Canonical']:20s}: {total:5d} lines ({percent:5.1f}% done)")
    
    print(f"\n{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description='Update project statistics')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without saving')
    args = parser.parse_args()
    
    # Paths
    project_root = Path(__file__).parent.parent.parent
    all_lines_csv = project_root / 'data' / 'all_lines.csv'
    characters_csv = project_root / 'data' / 'characters.csv'
    build_dir = project_root / 'build' / 'OGG'
    
    print(f"\n{'='*70}")
    print(f"UPDATE PROJECT STATISTICS")
    print(f"{'='*70}\n")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if args.dry_run:
        print(f"Mode: DRY RUN (no files will be modified)")
    else:
        print(f"Mode: LIVE UPDATE")
    
    print(f"\n{'='*70}\n")
    
    # Load data
    lines_by_speaker = load_all_lines(all_lines_csv)
    characters = load_characters(characters_csv)
    synthesized = count_synthesized_files(build_dir)
    
    # Map speakers to characters
    speaker_to_character = map_speakers_to_characters(characters, lines_by_speaker)
    
    # Calculate stats
    updated_characters = calculate_character_stats(
        characters,
        lines_by_speaker,
        speaker_to_character,
        synthesized
    )
    
    # Save
    save_characters(characters_csv, updated_characters, dry_run=args.dry_run)
    
    # Summary
    generate_summary_report(updated_characters)
    
    if args.dry_run:
        print("[i] This was a dry run. Run without --dry-run to save changes.\n")
    else:
        print("[+] Statistics updated successfully!\n")


if __name__ == '__main__':
    main()
