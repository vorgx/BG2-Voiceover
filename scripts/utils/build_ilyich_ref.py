"""
Build Ilyich voice reference from ElevenLabs generated audio.
Ilyich is a duergar (evil dwarf) dungeon leader - gruff and aggressive.
Using custom ElevenLabs voice sample.
"""
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ELEVENLABS_SOURCE = ROOT / "BG2 Files" / "Character Samples from Elevenlabs" / "ilyic v3.mp3"
OUTPUT = ROOT / "refs" / "ilyich_ref.wav"

def convert_mp3_to_wav(mp3_path: Path, wav_path: Path) -> None:
    """Convert MP3 to WAV format using pydub"""
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_mp3(str(mp3_path))
        audio.export(str(wav_path), format="wav")
    except ImportError:
        # Fallback to librosa if pydub not available
        import librosa
        import soundfile as sf
        audio, sr = librosa.load(str(mp3_path), sr=None)
        sf.write(str(wav_path), audio, sr)

def get_duration(wav_path: Path) -> float:
    with wave.open(str(wav_path), 'rb') as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        return frames / float(rate)

def main():
    print("🎤 Building Ilyich Voice Reference")
    print(f"   Using ElevenLabs generated audio\n")
    
    if not ELEVENLABS_SOURCE.exists():
        print(f"   ✗ Source file not found: {ELEVENLABS_SOURCE}")
        return
    
    print(f"   ✓ Found: {ELEVENLABS_SOURCE.name}")
    
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert MP3 to WAV
    print(f"   Converting MP3 to WAV...")
    convert_mp3_to_wav(ELEVENLABS_SOURCE, OUTPUT)
    
    duration = get_duration(OUTPUT)
    print(f"   Duration: {duration:.1f} seconds")
    print(f"\n✅ Ilyich reference ready at: refs/ilyich_ref.wav")

if __name__ == "__main__":
    main()
