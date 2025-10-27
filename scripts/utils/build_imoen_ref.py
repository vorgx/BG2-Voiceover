"""
Build Imoen voice reference from selected BG2 audio clips.
Based on successful Jaheira/Minsc approach: ~30 seconds, 5-8 diverse clips.
"""
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BG2_AUDIO = ROOT / "BG2 Files"
OUTPUT = ROOT / "refs" / "imoen_ref.wav"

# Selected clips for Imoen's voice reference
# Choose clips that showcase her cheery, bright personality
# Aim for ~30 seconds total
SELECTED_CLIPS = [
    "IMOEN01.WAV",
    "IMOEN02.WAV",
    "IMOEN03.WAV",
    "IMOEN04.WAV",
    "IMOEN05.WAV",
    "IMOEN06.WAV",
    "IMOEN07.WAV",
    "IMOEN08.WAV",
    "IMOEN09.WAV",
    "IMOEN10.WAV",
    "IMOEN11.WAV",
    "IMOEN12.WAV",
    "IMOEN13.WAV",
    "IMOEN14.WAV",
    "IMOEN15.WAV",
    "IMOEN16.WAV",
    "IMOEN17.WAV",
    "IMOEN18.WAV",
    "IMOEN19.WAV",
    "IMOEN20.WAV",
]

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

def concatenate_wavs(wav_files: list[Path], output_path: Path) -> None:
    """Concatenate multiple WAV files into one."""
    # Read parameters from first file
    with wave.open(str(wav_files[0]), 'rb') as first:
        params = first.getparams()
    
    # Write concatenated output
    with wave.open(str(output_path), 'wb') as output:
        output.setparams(params)
        
        for wav_file in wav_files:
            with wave.open(str(wav_file), 'rb') as wf:
                output.writeframes(wf.readframes(wf.getnframes()))
    
    print(f"✅ Created: {output_path}")
    print(f"   Duration: {get_duration(output_path):.1f} seconds")

def main():
    print("🎤 Building Imoen Voice Reference")
    print(f"   Target: ~30 seconds from {len(SELECTED_CLIPS)} clips\n")
    
    # Find all clip files
    wav_paths = []
    total_duration = 0.0
    
    for clip_name in SELECTED_CLIPS:
        try:
            path = find_wav(clip_name)
            duration = get_duration(path)
            wav_paths.append(path)
            total_duration += duration
            print(f"   ✓ {clip_name:15} {duration:5.2f}s")
        except FileNotFoundError as e:
            print(f"   ✗ {e}")
            return
    
    print(f"\n   Total duration: {total_duration:.2f} seconds")
    
    # Create output
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    concatenate_wavs(wav_paths, OUTPUT)
    print(f"\n✅ Imoen reference ready at: refs/imoen_ref.wav")

if __name__ == "__main__":
    main()
