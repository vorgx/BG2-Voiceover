"""
Preview Imoen audio files to select best reference samples.
Plays audio files and helps you choose the clearest ones.
"""

import pathlib
import subprocess
import wave

# Imoen's voice files identified from dialog.tra
IMOEN_CANDIDATES = [
    # Format: (filename_without_OH, description, emotion)
    ("IMOEN01.WAV", "Wake up, you! Wake up! Come on, we have to get outta here!", "urgent/panicked"),
    ("IMOEN02.WAV", "No, no! No, I'm not gonna end up dead in this place!", "fearful"),
    ("IMOEN03.WAV", "Yep?", "neutral/casual"),
    ("IMOEN04.WAV", "Whatcha want?", "casual"),
    ("IMOEN05.WAV", "I'll stick with you no matter what...", "supportive"),
    ("IMOEN06.WAV", "Ye're a queer fellow.", "teasing"),
    ("IMOEN08.WAV", "Aww, come on. I'm not cut out for the leadership stuff.", "reluctant"),
    ("IMOEN09.WAV", "*yawn* I'm getting sleepy. Wish we could stop for a bit.", "tired"),
    ("IMOEN10.WAV", "If we're going to do nothing, let's at least find a safer place to do it.", "practical"),
    ("IMOEN12.WAV", "My blade will cut you down to size!", "battle/aggressive"),
    ("IMOEN13.WAV", "If I have to fight to get out of here, so be it!", "determined"),
    ("IMOEN14.WAV", "Poor sod, takin' the dirt-nap so soon.", "casual/dark humor"),
    ("IMOEN15.WAV", "Heya! It's me, Imoen.", "cheerful/greeting"),
    ("IMOEN20.WAV", "Come on, now, don't let me suffer in this place...", "pleading"),
    ("IMOEN22.WAV", "I wish I could spend more time in the forest. Oh, it feels so alive!", "wistful/happy"),
    ("IMOEN23.WAV", "I don't feel like I fit in with the people in the city anymore.", "sad/introspective"),
    ("IMOEN24.WAV", "This place is just too darn creepy. I really want out of here.", "nervous"),
    ("IMOEN26.WAV", "Might as well be up and about. I don't think I'd sleep anyway.", "restless"),
    ("IMOEN33.WAV", "Gotcha.", "acknowledgment"),
    ("IMOEN34.WAV", "Good to go.", "ready"),
    ("IMOEN35.WAV", "Right you are.", "agreement"),
    ("IMOEN36.WAV", "All right, all right.", "compliance"),
    ("IMOEN37.WAV", "No problem at all.", "helpful"),
    ("IMOEN38.WAV", "You can count on me!", "enthusiastic"),
    ("IMOEN39.WAV", "This way then?", "questioning"),
]

def get_audio_info(wav_path):
    """Get duration and format info from WAV file."""
    try:
        with wave.open(str(wav_path), 'rb') as wav:
            frames = wav.getnframes()
            rate = wav.getframerate()
            duration = frames / float(rate)
            channels = wav.getnchannels()
            sampwidth = wav.getsampwidth()
            return {
                'duration': duration,
                'sample_rate': rate,
                'channels': channels,
                'bit_depth': sampwidth * 8,
                'exists': True
            }
    except Exception as e:
        return {'exists': False, 'error': str(e)}

def play_audio(wav_path):
    """Play audio file using Windows Media Player."""
    try:
        # Use Start-Process in PowerShell to play without blocking
        subprocess.run([
            'powershell', '-Command',
            f'Start-Process "{wav_path}"'
        ], check=True)
        return True
    except Exception as e:
        print(f"  Error playing: {e}")
        return False

def preview_files():
    """Preview all Imoen audio files."""
    wav_dir = pathlib.Path(r"C:\Users\tenod\source\repos\BG2 Voiceover\BG2 Files\WAV Files")
    
    print("=" * 80)
    print("IMOEN VOICE FILE PREVIEW")
    print("=" * 80)
    print("\nThis will help you select 5-10 files for creating a better reference.")
    print("\nSelection criteria:")
    print("  ✓ Clear audio (no background noise)")
    print("  ✓ Variety of emotions")
    print("  ✓ Total ~20-30 seconds")
    print("  ✓ Natural speaking pace\n")
    
    available_files = []
    
    for filename, text, emotion in IMOEN_CANDIDATES:
        wav_path = wav_dir / ("OH" + filename)
        info = get_audio_info(wav_path)
        
        if not info['exists']:
            continue
            
        available_files.append((filename, text, emotion, info))
        
        print(f"\n{'='*80}")
        print(f"FILE: {filename}")
        print(f"TEXT: {text}")
        print(f"EMOTION: {emotion}")
        print(f"DURATION: {info['duration']:.2f}s")
        print(f"FORMAT: {info['channels']} ch, {info['bit_depth']}-bit, {info['sample_rate']} Hz")
        print(f"PATH: {wav_path}")
    
    print(f"\n{'='*80}")
    print(f"\nFound {len(available_files)} Imoen audio files")
    print(f"Total duration: {sum(f[3]['duration'] for f in available_files):.2f} seconds")
    
    # Provide recommendations
    print("\n" + "="*80)
    print("RECOMMENDED SELECTION (for balanced reference):")
    print("="*80)
    
    recommendations = [
        ("IMOEN15.WAV", "Cheerful greeting - her iconic line"),
        ("IMOEN22.WAV", "Happy/wistful - longer sentence"),
        ("IMOEN05.WAV", "Supportive - shows caring side"),
        ("IMOEN24.WAV", "Nervous - different emotion"),
        ("IMOEN38.WAV", "Enthusiastic - energetic"),
        ("IMOEN36.WAV", "Neutral compliance - calm"),
    ]
    
    total_recommended = 0
    for filename, reason in recommendations:
        match = next((f for f in available_files if f[0] == filename), None)
        if match:
            duration = match[3]['duration']
            total_recommended += duration
            print(f"  • {filename:<15} ({duration:>4.1f}s) - {reason}")
    
    print(f"\n  Total: {total_recommended:.1f} seconds (ideal range: 20-30s)")
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Listen to recommended files:")
    for filename, _ in recommendations:
        wav_path = wav_dir / ("OH" + filename)
        print(f'   Start-Process "{wav_path}"')
    
    print("\n2. Edit scripts/create_reference.py and update imoen_strrefs list:")
    print("   imoen_strrefs = [")
    for filename, _ in recommendations:
        print(f'       "OH{filename}",')
    print("   ]")
    
    print("\n3. Run: python scripts/create_reference.py")
    print("4. Update data/voices.json to use refs/imoen_ref_multi.wav")

if __name__ == "__main__":
    preview_files()
