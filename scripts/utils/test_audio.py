"""
Quick audio playback test for comparing voice quality
"""
import wave
import subprocess
import sys

def get_audio_info(filepath):
    """Get basic info about a WAV file"""
    try:
        with wave.open(filepath, 'rb') as wf:
            channels = wf.getnchannels()
            width = wf.getsampwidth()
            rate = wf.getframerate()
            frames = wf.getnframes()
            duration = frames / rate
            
            return {
                'channels': channels,
                'sample_width': width * 8,
                'sample_rate': rate,
                'duration': f"{duration:.2f}s"
            }
    except Exception as e:
        return {'error': str(e)}

def play_audio(filepath):
    """Play audio file using Windows Media Player"""
    try:
        subprocess.run(['powershell', '-Command', f'Start-Process "{filepath}"'], check=True)
        return True
    except:
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("BG2 VOICEOVER - Audio Quality Test")
    print("=" * 60)
    print()
    
    # Check reference audio
    ref_path = r"C:\Users\tenod\source\repos\BG2 Voiceover\refs\imoen_ref_multi.wav"
    print(f"📁 Reference Audio: {ref_path}")
    info = get_audio_info(ref_path)
    for key, value in info.items():
        print(f"   {key}: {value}")
    print()
    
    # Check synthesized audio
    synth_path = r"C:\Users\tenod\source\repos\BG2 Voiceover\build\OGG\38606.wav"
    print(f"📁 Synthesized Audio: {synth_path}")
    info = get_audio_info(synth_path)
    for key, value in info.items():
        print(f"   {key}: {value}")
    print()
    
    # Check game audio
    game_path = r"E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition\lang\en_US\sounds\OH38606.wav"
    print(f"📁 Game Audio: {game_path}")
    info = get_audio_info(game_path)
    for key, value in info.items():
        print(f"   {key}: {value}")
    print()
    
    print("=" * 60)
    print("Would you like to play the synthesized audio? (Y/N)")
    response = input("> ").strip().upper()
    
    if response == 'Y':
        print("Playing audio...")
        play_audio(synth_path)
        print("✓ Audio playback started")
    else:
        print("Skipped playback")
