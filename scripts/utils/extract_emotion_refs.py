"""
Emotion Reference Audio Library Builder

Helps build a curated library of emotion reference audio clips from original
game WAV files. These clips are used as emotion prompts for Index-TTS synthesis
of vocalizations.

Workflow:
1. Scan original game WAV files
2. Prompt user to classify each as an emotion type (or skip)
3. Copy classified clips to refs/emotions/<character>/<emotion_type>.wav
4. Generate emotion_refs.json mapping file

Usage:
    python scripts/utils/extract_emotion_refs.py --character Jaheira
    python scripts/utils/extract_emotion_refs.py --character Minsc --auto-detect
"""

import argparse
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import subprocess

# Add parent to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.utils.classify_vocalizations import VocalizationType, classify_text


class EmotionRefBuilder:
    """Build emotion reference audio library."""
    
    def __init__(self, base_path: Path, refs_path: Path):
        """
        Initialize builder.
        
        Args:
            base_path: Base path to BG2 Voiceover project
            refs_path: Path to refs/emotions directory
        """
        self.base_path = base_path
        self.refs_path = refs_path
        self.refs_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing mapping if present
        self.mapping_file = refs_path / "emotion_refs.json"
        self.mapping = self._load_mapping()
    
    def _load_mapping(self) -> Dict:
        """Load existing emotion reference mapping."""
        if self.mapping_file.exists():
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_mapping(self):
        """Save emotion reference mapping."""
        with open(self.mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.mapping, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] Saved mapping to {self.mapping_file}")
    
    def _get_audio_duration(self, wav_path: Path) -> float:
        """Get audio duration in seconds (requires ffprobe)."""
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', str(wav_path)],
                capture_output=True,
                text=True,
                check=True
            )
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
            return 0.0
    
    def _play_audio(self, wav_path: Path):
        """Play audio file (Windows)."""
        try:
            # Use PowerShell to play audio
            subprocess.run(
                ['powershell', '-c', f'(New-Object Media.SoundPlayer "{wav_path}").PlaySync()'],
                check=False,
                timeout=10
            )
        except Exception as e:
            print(f"[!] Could not play audio: {e}")
    
    def extract_for_character(
        self,
        character: str,
        wav_dir: Path,
        all_lines_csv: Path,
        characters_csv: Path,
        auto_detect: bool = False
    ):
        """
        Extract emotion references for a character.
        
        Args:
            character: Character name (e.g., "Jaheira")
            wav_dir: Directory containing original game WAV files
            all_lines_csv: Path to all_lines.csv with Original_VO_WAV column
            characters_csv: Path to characters.csv with character mapping
            auto_detect: Auto-detect vocalizations using classifier
        """
        print(f"\n{'='*60}")
        print(f"Extracting Emotion References: {character}")
        print(f"{'='*60}\n")
        
        # Load character lines with Original_VO_WAV mapping
        lines_map = self._load_lines_csv(all_lines_csv, characters_csv, character)
        print(f"Loaded {len(lines_map)} voiced lines for {character} from {all_lines_csv.name}")
        
        # Create character emotion directory
        char_emotions_dir = self.refs_path / character.lower()
        char_emotions_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize character mapping
        if character not in self.mapping:
            self.mapping[character] = {}
        
        processed = 0
        added = 0
        skipped = 0
        
        # Process each voice file
        for original_vo_wav, (strref_int, text) in sorted(lines_map.items()):
            # Find the corresponding WAV file
            # Original_VO_WAV like "JAHEIR01", need to add .WAV extension
            wav_file = wav_dir / f"{original_vo_wav}.WAV"
            if not wav_file.exists():
                # Try lowercase
                wav_file = wav_dir / f"{original_vo_wav}.wav"
                if not wav_file.exists():
                    continue
            
            processed += 1
            emotion_type = None
            confidence = 0.0
            
            # Auto-detect vocalization?
            if auto_detect:
                voc_result = classify_text(text, min_confidence=0.7)
                if not voc_result or not voc_result.get('is_pure'):
                    skipped += 1
                    continue  # Skip non-vocalizations
                
                emotion_type = voc_result['type'].value
                confidence = voc_result['confidence']
                print(f"\n[Auto-detected] StrRef {strref_int}: '{text}'")
                print(f"  Type: {emotion_type} (confidence: {confidence:.2f})")
            else:
                # Manual classification
                print(f"\n[{processed}/{len(lines_map)}] StrRef {strref_int}: '{text}'")
                print(f"  WAV: {wav_file.name}")
                
                # Show options
                print("\nEmotion Types:")
                print("  1. grunt    2. scream   3. moan     4. yell")
                print("  5. gasp     6. laugh    7. cry      8. cough")
                print("  9. sigh     0. generic  s. skip     q. quit")
                
                choice = input("\nClassify as (1-9,0,s,q) [s]: ").strip().lower()
                
                if choice == 'q':
                    break
                if choice == '' or choice == 's':
                    skipped += 1
                    continue
                
                # Map choice to emotion type
                type_map = {
                    '1': 'grunt', '2': 'scream', '3': 'moan', '4': 'yell',
                    '5': 'gasp', '6': 'laugh', '7': 'cry', '8': 'cough',
                    '9': 'sigh', '0': 'generic'
                }
                emotion_type = type_map.get(choice)
                if not emotion_type:
                    print("Invalid choice, skipping.")
                    skipped += 1
                    continue
            
            # Copy WAV to emotion refs
            dest_file = char_emotions_dir / f"{emotion_type}_{strref_int}.wav"
            shutil.copy2(wav_file, dest_file)
            
            # Add to mapping
            if emotion_type not in self.mapping[character]:
                self.mapping[character][emotion_type] = []
            
            self.mapping[character][emotion_type].append({
                'strref': strref_int,
                'text': text,
                'file': str(dest_file.relative_to(self.base_path)).replace('\\', '/'),
                'duration': self._get_audio_duration(dest_file)
            })
            
            added += 1
            print(f"  [+] Added as {emotion_type} reference")
            
            # Auto-save every 10 additions
            if added % 10 == 0:
                self._save_mapping()
        
        # Final save
        self._save_mapping()
        
        print(f"\n{'='*60}")
        print(f"Summary for {character}:")
        print(f"  Processed: {processed}")
        print(f"  Added: {added}")
        print(f"  Skipped: {skipped}")
        print(f"{'='*60}\n")
    
    def _load_lines_csv(self, all_lines_csv: Path, characters_csv: Path, character: str) -> Dict[str, tuple]:
        """
        Load Original_VO_WAV -> (StrRef, Text) mapping from all_lines.csv for a character.
        
        Args:
            all_lines_csv: Path to all_lines.csv
            characters_csv: Path to characters.csv
            character: Character name to filter by
            
        Returns:
            Dict mapping Original_VO_WAV (e.g., "JAHEIR01") to (strref, text) tuple
        """
        import csv
        
        # Load character DLGFiles mapping
        char_dlg_files = set()
        with open(characters_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                canonical = row.get('Canonical', '').strip()
                if canonical.lower() == character.lower():
                    dlg_files = row.get('DLGFiles', '').strip()
                    if dlg_files:
                        # Split by pipe and store with .DLG extension
                        for dlg in dlg_files.split('|'):
                            dlg_clean = dlg.strip().upper()
                            # Ensure .DLG extension is present
                            if not dlg_clean.endswith('.DLG'):
                                dlg_clean = dlg_clean + '.DLG'
                            char_dlg_files.add(dlg_clean)
                    break
        
        if not char_dlg_files:
            print(f"[!] No DLGFiles found for {character} in {characters_csv}")
            return {}
        
        print(f"   Looking for speakers: {', '.join(sorted(char_dlg_files))}")
        
        # Load lines from all_lines.csv
        lines = {}
        with open(all_lines_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Check if this line's DLG_File matches the character's DLGFiles
                    dlg_file = row.get('DLG_File', '').strip().upper()
                    if not dlg_file:
                        continue
                    
                    # Add .DLG extension for matching against char_dlg_files
                    dlg_file_with_ext = dlg_file + '.DLG' if not dlg_file.endswith('.DLG') else dlg_file
                    
                    if dlg_file_with_ext not in char_dlg_files:
                        continue
                    
                    # Get Original_VO_WAV column
                    wav_ref = row.get('Original_VO_WAV', '').strip()
                    if not wav_ref:
                        continue
                    
                    strref = int(row['StrRef'])
                    text = row['Text'].strip()
                    if text:
                        lines[wav_ref] = (strref, text)
                except (ValueError, KeyError):
                    continue
        
        return lines
    
    def show_summary(self):
        """Show summary of current emotion references."""
        print(f"\n{'='*60}")
        print("Emotion Reference Library Summary")
        print(f"{'='*60}\n")
        
        if not self.mapping:
            print("No emotion references found.")
            return
        
        for character, emotions in sorted(self.mapping.items()):
            print(f"\n{character}:")
            for emotion_type, refs in sorted(emotions.items()):
                print(f"  {emotion_type}: {len(refs)} clips")
                for ref in refs[:3]:  # Show first 3
                    print(f"    - {ref['strref']}: '{ref['text'][:40]}...'")
                if len(refs) > 3:
                    print(f"    ... and {len(refs)-3} more")
        
        print(f"\n{'='*60}\n")
    
    def create_generic_fallbacks(self):
        """Create generic emotion fallback references."""
        print("\n[*] Creating generic fallback references...")
        
        # For each character, create 'generic_<emotion>' fallbacks
        for character in self.mapping:
            for emotion_type in VocalizationType:
                emotion = emotion_type.value
                if emotion in self.mapping[character] and self.mapping[character][emotion]:
                    # Use first clip as generic fallback
                    first_ref = self.mapping[character][emotion][0]
                    
                    # Create generic reference
                    generic_key = f"generic_{emotion}"
                    if generic_key not in self.mapping[character]:
                        self.mapping[character][generic_key] = first_ref
                        print(f"  [+] {character}: generic_{emotion} -> {first_ref['strref']}")
        
        self._save_mapping()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build emotion reference audio library"
    )
    parser.add_argument(
        '--character',
        required=True,
        help="Character name (e.g., Jaheira)"
    )
    parser.add_argument(
        '--wav-dir',
        type=Path,
        help="Directory with original WAV files (default: BG2 Files/WAV Files)"
    )
    parser.add_argument(
        '--all-lines-csv',
        type=Path,
        help="CSV with StrRef,Speaker,Text,Original_VO_WAV mapping (default: data/all_lines.csv)"
    )
    parser.add_argument(
        '--characters-csv',
        type=Path,
        help="CSV with character mapping (default: data/characters.csv)"
    )
    parser.add_argument(
        '--auto-detect',
        action='store_true',
        help="Auto-detect vocalizations using classifier"
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help="Show summary of current emotion references and exit"
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    base_path = Path(__file__).parent.parent.parent
    refs_path = base_path / "refs" / "emotions"
    
    builder = EmotionRefBuilder(base_path, refs_path)
    
    # Show summary if requested
    if args.summary:
        builder.show_summary()
        return
    
    # Default paths
    wav_dir = args.wav_dir or (base_path / "BG2 Files" / "WAV Files")
    all_lines_csv = args.all_lines_csv or (base_path / "data" / "all_lines.csv")
    characters_csv = args.characters_csv or (base_path / "data" / "characters.csv")
    
    # Validate paths
    if not wav_dir.exists():
        print(f"[X] WAV directory not found: {wav_dir}")
        return
    if not all_lines_csv.exists():
        print(f"[X] Lines CSV not found: {all_lines_csv}")
        return
    if not characters_csv.exists():
        print(f"[X] Characters CSV not found: {characters_csv}")
        return
    
    # Extract references
    builder.extract_for_character(
        args.character,
        wav_dir,
        all_lines_csv,
        characters_csv,
        auto_detect=args.auto_detect
    )
    
    # Create generic fallbacks
    builder.create_generic_fallbacks()
    
    # Show summary
    builder.show_summary()


if __name__ == "__main__":
    main()
