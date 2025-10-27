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
        print(f"\n✅ Saved mapping to {self.mapping_file}")
    
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
            print(f"⚠️ Could not play audio: {e}")
    
    def extract_for_character(
        self,
        character: str,
        wav_dir: Path,
        lines_csv: Path,
        auto_detect: bool = False
    ):
        """
        Extract emotion references for a character.
        
        Args:
            character: Character name (e.g., "Jaheira")
            wav_dir: Directory containing original game WAV files
            lines_csv: CSV file with StrRef,Text mapping
            auto_detect: Auto-detect vocalizations using classifier
        """
        print(f"\n{'='*60}")
        print(f"Extracting Emotion References: {character}")
        print(f"{'='*60}\n")
        
        # Load character lines
        lines_map = self._load_lines_csv(lines_csv)
        print(f"Loaded {len(lines_map)} lines from {lines_csv.name}")
        
        # Create character emotion directory
        char_emotions_dir = self.refs_path / character.lower()
        char_emotions_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize character mapping
        if character not in self.mapping:
            self.mapping[character] = {}
        
        # Scan for existing WAV files
        wav_files = sorted(wav_dir.glob("*.wav"))
        print(f"Found {len(wav_files)} WAV files in {wav_dir}\n")
        
        processed = 0
        added = 0
        skipped = 0
        
        for wav_file in wav_files:
            # Get StrRef from filename
            try:
                strref = wav_file.stem
                if not strref.isdigit():
                    continue
                strref_int = int(strref)
            except ValueError:
                continue
            
            # Get text for this StrRef
            text = lines_map.get(strref_int)
            if not text:
                continue
            
            processed += 1
            
            # Auto-detect vocalization?
            if auto_detect:
                voc_result = classify_text(text, min_confidence=0.7)
                if not voc_result or not voc_result.get('is_pure'):
                    continue  # Skip non-vocalizations
                
                emotion_type = voc_result['type'].value
                confidence = voc_result['confidence']
                print(f"\n[Auto-detected] StrRef {strref}: '{text}'")
                print(f"  Type: {emotion_type} (confidence: {confidence:.2f})")
            else:
                # Manual classification
                print(f"\n[{processed}/{len(lines_map)}] StrRef {strref}: '{text}'")
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
            dest_file = char_emotions_dir / f"{emotion_type}_{strref}.wav"
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
            print(f"  ✅ Added as {emotion_type} reference")
            
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
    
    def _load_lines_csv(self, csv_path: Path) -> Dict[int, str]:
        """Load StrRef -> Text mapping from CSV."""
        import csv
        
        lines = {}
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    strref = int(row['StrRef'])
                    text = row['Text'].strip()
                    if text:
                        lines[strref] = text
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
        print("\n📝 Creating generic fallback references...")
        
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
                        print(f"  ✅ {character}: generic_{emotion} -> {first_ref['strref']}")
        
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
        '--lines-csv',
        type=Path,
        help="CSV with StrRef,Text mapping (default: data/chapter1_split/<character>_lines.csv)"
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
    lines_csv = args.lines_csv or (
        base_path / "data" / "chapter1_split" / f"{args.character.lower()}_lines.csv"
    )
    
    # Validate paths
    if not wav_dir.exists():
        print(f"❌ WAV directory not found: {wav_dir}")
        return
    if not lines_csv.exists():
        print(f"❌ Lines CSV not found: {lines_csv}")
        return
    
    # Extract references
    builder.extract_for_character(
        args.character,
        wav_dir,
        lines_csv,
        auto_detect=args.auto_detect
    )
    
    # Create generic fallbacks
    builder.create_generic_fallbacks()
    
    # Show summary
    builder.show_summary()


if __name__ == "__main__":
    main()
