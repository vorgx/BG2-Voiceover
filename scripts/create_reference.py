"""
Create improved reference audio by concatenating multiple character lines.
This gives Index-TTS better voice characteristics to clone from.
"""

import wave
import pathlib
import struct

def concatenate_wav_files(input_files, output_file):
    """
    Concatenate multiple WAV files into a single reference file.
    All inputs must have the same sample rate, channels, and bit depth.
    """
    # Read first file to get parameters
    with wave.open(str(input_files[0]), 'rb') as first_wav:
        params = first_wav.getparams()
        frames = []
        
        # Read all files
        for wav_file in input_files:
            with wave.open(str(wav_file), 'rb') as wav:
                if wav.getparams()[:3] != params[:3]:  # Check format compatibility
                    print(f"Warning: {wav_file} has different format, skipping")
                    continue
                frames.append(wav.readframes(wav.getnframes()))
        
        # Write concatenated output
        with wave.open(str(output_file), 'wb') as out_wav:
            out_wav.setparams(params)
            for frame_data in frames:
                out_wav.writeframes(frame_data)
    
    print(f"Created reference file: {output_file}")
    print(f"  Combined {len(input_files)} audio files")
    
    # Get duration
    with wave.open(str(output_file), 'rb') as wav:
        duration = wav.getnframes() / wav.getframerate()
        print(f"  Total duration: {duration:.2f} seconds")


def create_imoen_reference():
    """
    Create enhanced Imoen reference from original BG2 audio files.
    
    Strategy: Use diverse samples that show different emotions and speaking styles.
    Recommended: 5-10 files, 15-30 seconds total duration.
    """
    bg2_wav_dir = pathlib.Path(r"C:\Users\tenod\source\repos\BG2 Voiceover\BG2 Files\WAV Files")
    output_dir = pathlib.Path(r"C:\Users\tenod\source\repos\BG2 Voiceover\refs")
    
    # These are example Imoen files - adjust based on which ones are actually hers
    # You'll need to identify which strrefs correspond to Imoen by cross-referencing
    # with dialog.tra or testing in-game
    
    # Selection criteria:
    # - Clear speech (no background noise/combat sounds)
    # - Variety of emotions (neutral, happy, concerned, sarcastic)
    # - Different sentence lengths
    # - Total ~20-30 seconds of audio
    
    # Recommended Imoen voice files for reference
    # Selected for clarity, emotional variety, and natural speaking
    # Total: ~21 seconds (ideal range: 20-30s)
    imoen_strrefs = [
        "IMOEN15.WAV",  # "Heya! It's me, Imoen." - Cheerful greeting (iconic) ~1.4s
        "IMOEN22.WAV",  # "I wish I could spend more time..." - Happy/wistful ~4.8s
        "IMOEN05.WAV",  # "I'll stick with you..." - Supportive, caring ~4.7s
        "IMOEN24.WAV",  # "This place is just too darn creepy..." - Nervous ~4.4s
        "IMOEN09.WAV",  # "*yawn* I'm getting sleepy..." - Tired ~3.5s (estimated)
        "IMOEN38.WAV",  # "You can count on me!" - Enthusiastic, energetic ~0.7s
        "IMOEN36.WAV",  # "All right, all right." - Neutral, calm ~1.2s
    ]
    
    if not imoen_strrefs:
        print("ERROR: No Imoen audio files specified!")
        print("\nTo find Imoen's voice files:")
        print("1. Check BG2 Files/dialog.tra for Imoen's string references")
        print("2. Look for patterns in the StrRef numbers (characters often have consecutive ranges)")
        print("3. Listen to WAV files in the 78000-82000 range (BG2 character audio)")
        print("4. Update imoen_strrefs list in this script")
        return
    
    # Build full paths
    input_files = [bg2_wav_dir / filename for filename in imoen_strrefs]
    
    # Verify all files exist
    missing = [f for f in input_files if not f.exists()]
    if missing:
        print(f"ERROR: Missing files: {missing}")
        return
    
    # Create output
    output_file = output_dir / "imoen_ref_multi.wav"
    concatenate_wav_files(input_files, output_file)
    
    print(f"\nUpdate voices.json to use this reference:")
    print(f'  "Imoen": "{str(output_file).replace(chr(92), chr(92)*2)}"')


if __name__ == "__main__":
    create_imoen_reference()
