"""
Post-process generated audio files with pitch and speed adjustments.

Uses pydub and numpy for audio manipulation without requiring external tools.
"""
import sys
import wave
import numpy as np
from pathlib import Path
from scipy import signal
import scipy.io.wavfile as wavfile

ROOT = Path(__file__).resolve().parents[2]


def change_speed(audio_data: np.ndarray, sample_rate: int, speed_factor: float) -> tuple[np.ndarray, int]:
    """
    Change audio speed by resampling.
    
    Args:
        audio_data: Audio samples as numpy array
        sample_rate: Original sample rate
        speed_factor: Speed multiplier (0.95 = slower, 1.05 = faster)
    
    Returns:
        Tuple of (modified audio data, new sample rate)
    """
    # Calculate new length
    new_length = int(len(audio_data) / speed_factor)
    
    # Resample audio
    resampled = signal.resample(audio_data, new_length)
    
    return resampled.astype(np.int16), sample_rate


def change_pitch(audio_data: np.ndarray, sample_rate: int, semitones: float) -> np.ndarray:
    """
    Change audio pitch by shifting frequency.
    
    Args:
        audio_data: Audio samples as numpy array
        sample_rate: Sample rate
        semitones: Number of semitones to shift (+2 = higher, -2 = lower)
    
    Returns:
        Modified audio data
    """
    # Calculate pitch shift ratio
    pitch_factor = 2 ** (semitones / 12.0)
    
    # Resample to shift pitch
    new_length = int(len(audio_data) / pitch_factor)
    shifted = signal.resample(audio_data, new_length)
    
    # Resample back to original length to maintain speed
    final = signal.resample(shifted, len(audio_data))
    
    return final.astype(np.int16)


def process_audio_file(
    input_path: Path,
    output_path: Path,
    speed: float | None = None,
    pitch_shift: float | None = None
) -> None:
    """
    Process a WAV file with speed and/or pitch adjustments.
    
    Args:
        input_path: Path to input WAV file
        output_path: Path to save modified WAV file
        speed: Speed multiplier (e.g., 0.95 for 5% slower)
        pitch_shift: Semitones to shift pitch (e.g., -2 for 2 semitones lower)
    """
    # Read audio file
    sample_rate, audio_data = wavfile.read(str(input_path))
    
    # Ensure 16-bit PCM
    if audio_data.dtype != np.int16:
        audio_data = (audio_data * 32767).astype(np.int16)
    
    # Apply speed change
    if speed and speed != 1.0:
        print(f"  Adjusting speed: {speed}x")
        audio_data, sample_rate = change_speed(audio_data, sample_rate, speed)
    
    # Apply pitch shift
    if pitch_shift and pitch_shift != 0:
        print(f"  Shifting pitch: {pitch_shift:+.1f} semitones")
        audio_data = change_pitch(audio_data, sample_rate, pitch_shift)
    
    # Write output file
    wavfile.write(str(output_path), sample_rate, audio_data)
    print(f"  ✓ Saved: {output_path}")


def main():
    """Process audio files based on voices.json configuration."""
    import json
    import csv
    
    if len(sys.argv) < 2:
        print("Usage: python adjust_audio.py <strref> [--speed 0.95] [--pitch -2]")
        print("   OR: python adjust_audio.py --speaker <SpeakerName>")
        print("   OR: python adjust_audio.py --batch <csv_file>")
        sys.exit(1)
    
    # Load voices.json to get speaker configurations
    voices_path = ROOT / "data" / "voices.json"
    with open(voices_path, 'r', encoding='utf-8') as f:
        voices = json.load(f)
    
    build_dir = ROOT / "build" / "OGG"
    
    # Parse arguments
    mode = sys.argv[1]
    
    if mode == "--speaker":
        # Process all files for a specific speaker
        speaker = sys.argv[2]
        voice_config = voices.get(speaker, {})
        
        speed = voice_config.get("speed")
        pitch_shift = voice_config.get("pitch_shift")
        
        if not speed and not pitch_shift:
            print(f"No speed or pitch_shift configured for {speaker}")
            sys.exit(0)
        
        print(f"Processing all files for speaker: {speaker}")
        print(f"  Speed: {speed if speed else 'unchanged'}")
        print(f"  Pitch: {pitch_shift if pitch_shift else 'unchanged'}")
        
        # Find all lines for this speaker
        lines_csv = ROOT / "data" / "chapter1_lines.csv"
        with open(lines_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                if row['Speaker'] == speaker:
                    strref = row['StrRef']
                    input_file = build_dir / f"{strref}.wav"
                    if input_file.exists():
                        output_file = build_dir / f"{strref}_adjusted.wav"
                        print(f"\n{strref}: {row['Text'][:60]}...")
                        process_audio_file(input_file, output_file, speed, pitch_shift)
                        # Replace original with adjusted
                        output_file.replace(input_file)
                        count += 1
        
        print(f"\n✅ Processed {count} files for {speaker}")
    
    elif mode == "--batch":
        # Process files from a CSV
        csv_file = Path(sys.argv[2])
        print(f"Processing batch from: {csv_file}")
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                speaker = row['Speaker']
                strref = row['StrRef']
                voice_config = voices.get(speaker, {})
                
                speed = voice_config.get("speed")
                pitch_shift = voice_config.get("pitch_shift")
                
                if speed or pitch_shift:
                    input_file = build_dir / f"{strref}.wav"
                    if input_file.exists():
                        output_file = build_dir / f"{strref}_adjusted.wav"
                        print(f"\n{speaker} - {strref}: {row['Text'][:60]}...")
                        process_audio_file(input_file, output_file, speed, pitch_shift)
                        output_file.replace(input_file)
    
    else:
        # Process single file with manual parameters
        strref = sys.argv[1]
        
        # Parse optional arguments
        speed = None
        pitch_shift = None
        
        for i, arg in enumerate(sys.argv[2:], start=2):
            if arg == "--speed" and i + 1 < len(sys.argv):
                speed = float(sys.argv[i + 1])
            elif arg == "--pitch" and i + 1 < len(sys.argv):
                pitch_shift = float(sys.argv[i + 1])
        
        input_file = build_dir / f"{strref}.wav"
        output_file = build_dir / f"{strref}_adjusted.wav"
        
        if not input_file.exists():
            print(f"File not found: {input_file}")
            sys.exit(1)
        
        print(f"Processing: {strref}")
        process_audio_file(input_file, output_file, speed, pitch_shift)
        output_file.replace(input_file)
        print(f"✅ Done!")


if __name__ == "__main__":
    main()
