"""Map all Chapter 1 speakers to characters.csv.

Extracts unique speakers from chapter1_lines.csv and adds any missing
characters to the characters.csv database.
"""
from __future__ import annotations

import csv
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
CHAPTER1_CSV = ROOT / "data" / "chapter1_lines.csv"
CHARACTERS_CSV = ROOT / "data" / "characters.csv"


def get_chapter1_speakers() -> dict[str, int]:
    """Get all speakers from Chapter 1 with line counts."""
    
    if not CHAPTER1_CSV.exists():
        print(f"❌ Chapter 1 file not found: {CHAPTER1_CSV}")
        return {}
    
    speakers = Counter()
    
    with CHAPTER1_CSV.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            speaker = row.get('Speaker', '').strip()
            if speaker:
                speakers[speaker] += 1
    
    return dict(speakers)


def load_existing_characters() -> set[str]:
    """Load existing character names and aliases from characters.csv."""
    
    if not CHARACTERS_CSV.exists():
        print(f"⚠️ Characters file not found: {CHARACTERS_CSV}")
        return set()
    
    known_characters = set()
    
    with CHARACTERS_CSV.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            canonical = row.get('Canonical', '').strip()
            aliases = row.get('Aliases', '').strip()
            
            if canonical:
                known_characters.add(canonical.upper())
            
            if aliases:
                for alias in aliases.split(';'):
                    known_characters.add(alias.strip().upper())
    
    return known_characters


def add_missing_characters(new_speakers: list[tuple[str, int]]):
    """Add missing speakers to characters.csv."""
    
    if not new_speakers:
        print("✅ All Chapter 1 speakers are already in characters.csv")
        return
    
    # Read existing characters
    with CHARACTERS_CSV.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        existing_rows = list(reader)
    
    # Add new characters
    for speaker, line_count in new_speakers:
        new_row = {
            'Canonical': speaker,
            'Aliases': '',
            'DLGFiles': '',
            'HasCanonicalVoice': 'Unknown',
            'Gender': '',
            'AgeBand': '',
            'Accent': '',
            'Archetype': '',
            'Energy': '',
            'Timbre': '',
            'Notes': f'Chapter 1 NPC - {line_count} lines',
            'VoicePreset': '',
            'RefFile': '',
            'Status': 'Draft'
        }
        existing_rows.append(new_row)
    
    # Write back
    with CHARACTERS_CSV.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_rows)
    
    print(f"✅ Added {len(new_speakers)} new characters to characters.csv")


def main():
    """Map Chapter 1 speakers to characters.csv."""
    
    print("🔍 Analyzing Chapter 1 speakers...\n")
    
    # Get Chapter 1 speakers
    chapter1_speakers = get_chapter1_speakers()
    
    if not chapter1_speakers:
        print("❌ No speakers found in Chapter 1")
        return
    
    print(f"Found {len(chapter1_speakers)} unique speakers in Chapter 1:")
    
    # Load existing characters
    known_characters = load_existing_characters()
    
    # Identify missing characters
    missing_speakers = []
    mapped_speakers = []
    
    for speaker, count in sorted(chapter1_speakers.items(), key=lambda x: x[1], reverse=True):
        if speaker.upper() in known_characters:
            mapped_speakers.append((speaker, count))
            print(f"   ✅ {speaker}: {count} lines (already in characters.csv)")
        else:
            missing_speakers.append((speaker, count))
            print(f"   ❌ {speaker}: {count} lines (NOT in characters.csv)")
    
    print(f"\n📊 Summary:")
    print(f"   Total speakers: {len(chapter1_speakers)}")
    print(f"   Already mapped: {len(mapped_speakers)}")
    print(f"   Missing: {len(missing_speakers)}")
    
    # Add missing characters
    if missing_speakers:
        print(f"\n📝 Adding missing characters to characters.csv...")
        add_missing_characters(missing_speakers)
        
        print(f"\n💡 Next steps:")
        print(f"   1. Review new entries in characters.csv")
        print(f"   2. Fill in character details (Gender, AgeBand, Archetype, etc.)")
        print(f"   3. Assign voice presets or reference files")
        print(f"   4. Update Status when ready for synthesis")
    else:
        print(f"\n✨ All speakers are mapped!")


if __name__ == "__main__":
    main()
