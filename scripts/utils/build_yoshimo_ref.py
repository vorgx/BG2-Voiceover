"""
Build Yoshimo voice reference from selected BG2 audio clips.
Charming bounty hunter - friendly but secretive, smooth timbre.
"""
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BG2_AUDIO = ROOT / "BG2 Files"
OUTPUT = ROOT / "refs" / "yoshimo_ref.wav"

# Selected clips for Yoshimo's voice reference
# Aim for ~30 seconds total
SELECTED_CLIPS = [
    "YOSHIM01.WAV",
    "YOSHIM02.WAV",
    "YOSHIM03.WAV",
    "YOSHIM04.WAV",
    "YOSHIM05.WAV",
    "YOSHIM06.WAV",
    "YOSHIM07.WAV",
    "YOSHIM08.WAV",
    "YOSHIM09.WAV",
    "YOSHIM10.WAV",
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
    with wave.open(str(wav_files[0]), 'rb') as first:
        params = first.getparams()
    
    with wave.open(str(output_path), 'wb') as output:
        output.setparams(params)
        
        for wav_file in wav_files:
            with wave.open(str(wav_file), 'rb') as wf:
                output.writeframes(wf.readframes(wf.getnframes()))
    
    print(f"✅ Created: {output_path}")
    print(f"   Duration: {get_duration(output_path):.1f} seconds")

def main():
    print("🎤 Building Yoshimo Voice Reference")
    print(f"   Target: ~30 seconds from {len(SELECTED_CLIPS)} clips\n")
    
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
    
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    concatenate_wavs(wav_paths, OUTPUT)
    print(f"\n✅ Yoshimo reference ready at: refs/yoshimo_ref.wav")

if __name__ == "__main__":
    main()
