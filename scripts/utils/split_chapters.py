"""Split all_lines.csv into separate chapter CSV files.

Creates chapter1_lines.csv through chapter7_lines.csv based on Chapter column.
Uses archive/data/dlg_chapter_map.csv for proper chapter assignment.
Lines without chapter assignment go to chapter_unassigned.csv
"""
from __future__ import annotations

import csv
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]
INPUT_CSV = ROOT / "data" / "all_lines.csv"
CHAPTER_MAP_CSV = ROOT / "archive" / "data" / "dlg_chapter_map.csv"
OUTPUT_DIR = ROOT / "data"


def load_chapter_mapping() -> dict[str, str]:
    """Load DLG file to chapter mapping from archive."""
    mapping = {}
    
    if not CHAPTER_MAP_CSV.exists():
        print(f"⚠️  Chapter map not found: {CHAPTER_MAP_CSV}")
        return mapping
    
    print(f"📖 Loading chapter mappings from {CHAPTER_MAP_CSV.name}...")
    
    with CHAPTER_MAP_CSV.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dlg_file = row['DLGFile'].replace('.DLG', '').upper()
            chapter = row['Chapter']
            mapping[dlg_file] = chapter
    
    print(f"   Loaded {len(mapping)} DLG file mappings")
    return mapping


def extract_chapter_number(chapter_str: str) -> int | None:
    """Extract chapter number from string like 'Chapter 1 - Irenicus Dungeon'."""
    if not chapter_str or chapter_str == 'Unassigned':
        return None
    
    # Try to extract number after "Chapter "
    if 'Chapter' in chapter_str:
        parts = chapter_str.split()
        for i, part in enumerate(parts):
            if part == 'Chapter' and i + 1 < len(parts):
                try:
                    return int(parts[i + 1])
                except ValueError:
                    pass
    
    return None


def split_by_chapter():
    """Split all_lines.csv into separate chapter files."""
    
    if not INPUT_CSV.exists():
        print(f"❌ Input file not found: {INPUT_CSV}")
        return
    
    # Load chapter mappings
    dlg_to_chapter = load_chapter_mapping()
    
    print(f"\n📖 Reading {INPUT_CSV}...")
    
    # Read all lines
    with INPUT_CSV.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        all_lines = list(reader)
    
    print(f"   Total lines: {len(all_lines)}")
    
    # Update chapter assignments based on mapping
    print(f"\n🔄 Updating chapter assignments...")
    updated_count = 0
    
    for line in all_lines:
        dlg_file = line.get('DLG_File', '').upper()
        if dlg_file in dlg_to_chapter:
            chapter_str = dlg_to_chapter[dlg_file]
            chapter_num = extract_chapter_number(chapter_str)
            if chapter_num:
                line['Chapter'] = str(chapter_num)
                updated_count += 1
    
    print(f"   Updated {updated_count} lines with chapter info")
    
    # Group by chapter
    chapters = defaultdict(list)
    
    for line in all_lines:
        chapter = line.get('Chapter', '').strip()
        if chapter and chapter.isdigit():
            chapters[int(chapter)].append(line)
        else:
            chapters['unassigned'].append(line)
    
    # Write chapter files
    print(f"\n📝 Creating chapter files...")
    
    for chapter_num in range(1, 8):  # Chapters 1-7
        chapter_lines = chapters.get(chapter_num, [])
        
        if chapter_lines:
            output_file = OUTPUT_DIR / f"chapter{chapter_num}_lines.csv"
            
            with output_file.open('w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(chapter_lines)
            
            # Count voiced vs unvoiced
            voiced = sum(1 for line in chapter_lines if line.get('Original_VO_WAV', ''))
            unvoiced = len(chapter_lines) - voiced
            
            print(f"   ✅ {output_file.name}")
            print(f"      Total: {len(chapter_lines)}, Voiced: {voiced}, Unvoiced: {unvoiced}")
        else:
            print(f"   ⚠️  Chapter {chapter_num}: No lines found")
    
    # Write unassigned lines
    unassigned_lines = chapters.get('unassigned', [])
    if unassigned_lines:
        output_file = OUTPUT_DIR / "chapter_unassigned.csv"
        
        with output_file.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(unassigned_lines)
        
        voiced = sum(1 for line in unassigned_lines if line.get('Original_VO_WAV', ''))
        unvoiced = len(unassigned_lines) - voiced
        
        print(f"\n   ✅ {output_file.name}")
        print(f"      Total: {len(unassigned_lines)}, Voiced: {voiced}, Unvoiced: {unvoiced}")
    
    # Summary
    print(f"\n📊 Summary:")
    total_assigned = sum(len(chapters[i]) for i in range(1, 8) if i in chapters)
    print(f"   Assigned to chapters: {total_assigned}")
    print(f"   Unassigned: {len(unassigned_lines)}")
    print(f"   Total: {len(all_lines)}")
    
    # Chapter breakdown
    print(f"\n📋 Chapter Breakdown:")
    for chapter_num in range(1, 8):
        count = len(chapters.get(chapter_num, []))
        if count > 0:
            voiced = sum(1 for line in chapters[chapter_num] if line.get('Original_VO_WAV', ''))
            print(f"   Chapter {chapter_num}: {count} lines ({voiced} voiced, {count - voiced} unvoiced)")


if __name__ == "__main__":
    split_by_chapter()
