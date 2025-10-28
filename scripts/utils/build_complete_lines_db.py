"""Build complete dialogue lines database from all .D files.

Extracts all SAY statements with StrRef, Speaker, Text, WAV reference, and Chapter.
Creates comprehensive CSV with all game dialogue.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
DIALOG_DIR = ROOT / "BG2 Files" / "Dialog Files"
DIALOG_TRA = ROOT / "BG2 Files" / "dialog.tra"
OUTPUT_CSV = ROOT / "data" / "all_lines.csv"

# Match: SAY #12345 /* ~text~ [WAVFILE] */ or SAY #12345 /* ~text~ */
SAY_PATTERN = re.compile(
    r'\bSAY\s+#(\d+)\s+/\*\s*~([^~]*)~\s*(?:\[([A-Z0-9_]+)\])?\s*\*/',
    re.DOTALL
)

# Chapter assignment based on area codes (approximate)
CHAPTER_AREAS = {
    1: ['AR0602', 'AR0603', 'AR0604', 'AR0605', 'AR0606', 'AR0607'],  # Irenicus Dungeon
    2: ['AR0300', 'AR0301', 'AR0302', 'AR0303', 'AR0304', 'AR0305', 'AR0306', 'AR0307', 'AR0308', 'AR0309'],  # Athkatla
    3: ['AR1000', 'AR1001', 'AR1002', 'AR1003', 'AR1004', 'AR1005'],  # Spellhold
    # Add more chapter mappings as needed
}

# Guess chapter from dialog file name
def guess_chapter_from_filename(filename: str) -> Optional[int]:
    """Guess chapter based on dialog filename patterns."""
    name_upper = filename.upper()
    
    # Chapter 1 - Irenicus Dungeon
    if any(x in name_upper for x in ['IMOEN10', 'JAHEIRA', 'MINSC', 'YOSHIMO', 'ILYICH', 'RIELEV', 'DRYAD']):
        return 1
    
    # Common companions appear throughout, default to "Multiple"
    if any(x in name_upper for x in ['AERIE', 'ANOMEN', 'EDWIN', 'VICONIA', 'KORGAN', 'KELDORN']):
        return None  # Multiple chapters
    
    return None


def extract_speaker_from_filename(filename: str) -> str:
    """Extract likely speaker name from dialog filename."""
    # Remove file extension
    base = filename.upper().replace('.D', '')
    
    # Common character mappings
    speaker_map = {
        'IMOEN': 'Imoen',
        'JAHEIRA': 'Jaheira',
        'MINSC': 'Minsc',
        'YOSHIMO': 'Yoshimo',
        'AERIE': 'Aerie',
        'ANOMEN': 'Anomen',
        'EDWIN': 'Edwin',
        'VICONIA': 'Viconia',
        'KORGAN': 'Korgan',
        'KELDORN': 'Keldorn',
        'MAZZY': 'Mazzy',
        'VALYGAR': 'Valygar',
        'NALIA': 'Nalia',
        'HAERDALIS': 'HaerDalis',
        'CERND': 'Cernd',
        'SAREVOK': 'Sarevok',
        'ILYICH': 'Ilyich',
        'RIELEV': 'Rielev',
    }
    
    for key, value in speaker_map.items():
        if key in base:
            return value
    
    # Return cleaned filename if no match
    return base.replace('PLAYER1', 'PC').replace('BIMOEN', 'Imoen')


def scan_all_dialog_files() -> List[Dict[str, str]]:
    """Scan all .D files and extract dialogue information."""
    all_lines = []
    
    if not DIALOG_DIR.exists():
        print(f"❌ Dialog directory not found: {DIALOG_DIR}")
        return all_lines
    
    d_files = sorted(DIALOG_DIR.glob("*.D"))
    print(f"🔍 Scanning {len(d_files)} .D files...")
    
    for d_file in d_files:
        try:
            content = d_file.read_text(encoding="utf-8", errors="ignore")
            speaker = extract_speaker_from_filename(d_file.stem)
            chapter = guess_chapter_from_filename(d_file.stem)
            
            for match in SAY_PATTERN.finditer(content):
                strref = match.group(1)
                text = match.group(2).strip()
                wav_ref = match.group(3) if match.group(3) else ''
                
                all_lines.append({
                    'StrRef': strref,
                    'Speaker': speaker,
                    'Text': text,
                    'Original_VO_WAV': wav_ref,
                    'Generated_VO_WAV': '',  # Will be populated by synthesis
                    'Chapter': str(chapter) if chapter else '',
                    'DLG_File': d_file.stem
                })
        
        except Exception as e:
            print(f"⚠️ Error reading {d_file.name}: {e}")
            continue
    
    return all_lines


def load_dialog_tra() -> Dict[int, str]:
    """Load text from dialog.tra file for StrRef lookup."""
    text_map = {}
    
    if not DIALOG_TRA.exists():
        print(f"⚠️ dialog.tra not found: {DIALOG_TRA}")
        return text_map
    
    print(f"📖 Loading dialog.tra...")
    
    try:
        content = DIALOG_TRA.read_text(encoding="utf-8", errors="ignore")
        # Match: @12345 = ~text~
        tra_pattern = re.compile(r'@(\d+)\s*=\s*~([^~]*)~', re.DOTALL)
        
        for match in tra_pattern.finditer(content):
            strref = int(match.group(1))
            text = match.group(2).strip()
            text_map[strref] = text
    
    except Exception as e:
        print(f"⚠️ Error reading dialog.tra: {e}")
    
    return text_map


def main():
    """Build complete dialogue database."""
    
    # Scan all .D files
    all_lines = scan_all_dialog_files()
    
    if not all_lines:
        print("❌ No dialogue lines found!")
        return
    
    print(f"✅ Extracted {len(all_lines)} dialogue lines")
    
    # Load dialog.tra for text lookup (if needed to fill missing text)
    tra_text = load_dialog_tra()
    
    # Fill in missing text from dialog.tra
    for line in all_lines:
        if not line['Text'] or line['Text'] == '':
            strref = int(line['StrRef'])
            if strref in tra_text:
                line['Text'] = tra_text[strref]
    
    # Sort by StrRef
    all_lines.sort(key=lambda x: int(x['StrRef']))
    
    # Write to CSV
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    
    with OUTPUT_CSV.open('w', encoding='utf-8', newline='') as f:
        fieldnames = ['StrRef', 'Speaker', 'Text', 'Original_VO_WAV', 'Generated_VO_WAV', 'Chapter', 'DLG_File']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_lines)
    
    print(f"\n✅ Created {OUTPUT_CSV}")
    print(f"   Total lines: {len(all_lines)}")
    
    # Statistics
    voiced_count = sum(1 for line in all_lines if line['Original_VO_WAV'])
    unvoiced_count = len(all_lines) - voiced_count
    chapter1_count = sum(1 for line in all_lines if line['Chapter'] == '1')
    
    print(f"\n📊 Statistics:")
    print(f"   Lines with voice acting: {voiced_count}")
    print(f"   Lines without voice acting: {unvoiced_count}")
    print(f"   Chapter 1 lines: {chapter1_count}")
    
    # Speaker breakdown
    speakers = {}
    for line in all_lines:
        speaker = line['Speaker']
        speakers[speaker] = speakers.get(speaker, 0) + 1
    
    print(f"\n👥 Top 10 Speakers:")
    for speaker, count in sorted(speakers.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {speaker}: {count} lines")
    
    # Show sample
    print(f"\n📋 Sample lines:")
    for line in all_lines[:5]:
        text_preview = line['Text'][:60] + "..." if len(line['Text']) > 60 else line['Text']
        wav = f" [{line['Original_VO_WAV']}]" if line['Original_VO_WAV'] else ""
        ch = f" (Ch {line['Chapter']})" if line['Chapter'] else ""
        print(f"   {line['StrRef']} ({line['Speaker']}){wav}{ch}: {text_preview}")


if __name__ == "__main__":
    main()
