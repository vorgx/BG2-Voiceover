"""
Build Valygar voice reference from selected BG2 audio clips.
Stoic ranger - withdrawn and anti-magic, flat timbre.
"""
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BG2_AUDIO = ROOT / "BG2 Files"
OUTPUT = ROOT / "refs" / "valygar_ref.wav"

# Selected clips for Valygar's voice reference
SELECTED_CLIPS = [
    "VALYGA01.WAV",
    "VALYGA02.WAV",
    "VALYGA03.WAV",
    "VALYGA04.WAV",
    "VALYGA05.WAV",
    "VALYGA06.WAV",
    "VALYGA07.WAV",
    "VALYGA08.WAV",
]

def find_wav(filename: str) -> Path:
    matches = list(BG2_AUDIO.rglob(filename))
    if not matches:
        raise FileNotFoundError(f"Could not find {filename}")
    return matches[0]

def get_duration(wav_path: Path) -> float:
    with wave.open(str(wav_path), 'rb') as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        return frames / float(rate)

def concatenate_wavs(wav_files: list[Path], output_path: Path) -> None:
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
    print("🎤 Building Valygar Voice Reference")
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
    print(f"\n✅ Valygar reference ready at: refs/valygar_ref.wav")

if __name__ == "__main__":
    main()
