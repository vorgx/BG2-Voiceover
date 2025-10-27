"""
Listen to Minsc audio clips to select the best ones for voice reference.
Run this to hear each clip and note which ones showcase his character best.
"""
import wave
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BG2_AUDIO = ROOT / "BG2 Files"

def find_wav(filename: str) -> Path:
    """Find WAV file in BG2 Files directory."""
    matches = list(BG2_AUDIO.rglob(filename))
    if not matches:
        raise FileNotFoundError(f"Could not find {filename}")
    return matches[0]

def get_duration(wav_path: Path) -> float:
    """Get duration of WAV file in seconds."""
    with wave.open(str(wav_path), 'rb') as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        return frames / float(rate)

def play_clip(wav_path: Path):
    """Play audio clip using Windows default player."""
    subprocess.run(["powershell", "-Command", f"(New-Object Media.SoundPlayer '{wav_path}').PlaySync()"], 
                   capture_output=True)

def main():
    print("🎤 Minsc Audio Clip Browser")
    print("=" * 60)
    print("\nListening to MINSC*.WAV files...")
    print("Note which clips best showcase his boisterous personality!\n")
    
    # Get all Minsc clips
    clips = sorted(BG2_AUDIO.rglob("MINSC*.WAV"))[:20]
    
    for i, clip_path in enumerate(clips, 1):
        duration = get_duration(clip_path)
        print(f"\n[{i}/20] {clip_path.name:15} ({duration:.2f}s)")
        print(f"      Playing... ", end="", flush=True)
        
        try:
            play_clip(clip_path)
            print("✓")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        if i < len(clips):
            response = input("      Press Enter for next, or 'q' to quit: ")
            if response.lower() == 'q':
                break
    
    print("\n" + "=" * 60)
    print("💡 TIP: Edit scripts/utils/build_minsc_ref.py")
    print("   Update SELECTED_CLIPS list with your chosen files")
    print("   Aim for ~30 seconds total (5-8 clips)")

if __name__ == "__main__":
    main()
