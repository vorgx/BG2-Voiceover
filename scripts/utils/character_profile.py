"""
Character Profile Generator
Automatically extracts dialogue, voice characteristics, and recommendations for any speaker.
"""
import csv
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
LINES_CSV = ROOT / "data" / "lines.csv"
CHAPTER1_CSV = ROOT / "data" / "chapter1_lines.csv"
VOICES_JSON = ROOT / "data" / "voices.json"
BG2_AUDIO = ROOT / "BG2 Files"

def analyze_dialogue_characteristics(lines: list[str]) -> dict:
    """Analyze dialogue to infer voice characteristics."""
    all_text = " ".join(lines).lower()
    
    characteristics = {
        "accent_indicators": [],
        "tone_indicators": [],
        "speech_patterns": []
    }
    
    # Accent indicators
    accent_patterns = {
        "Scottish": [r"laddie", r"'is\b", r"givin'", r"th'\b", r"ye\b", r"'em\b"],
        "Theatrical": [r"dost", r"thou", r"thee", r"forsooth", r"'tis"],
        "Upper-class": [r"indeed", r"quite", r"rather", r"certainly"],
        "Archaic/Formal": [r"shall", r"thee", r"thy", r"doth"]
    }
    
    for accent, patterns in accent_patterns.items():
        if any(re.search(pattern, all_text) for pattern in patterns):
            characteristics["accent_indicators"].append(accent)
    
    # Tone indicators
    if re.search(r"!\s*[A-Z]", " ".join(lines)):  # Multiple exclamations
        characteristics["tone_indicators"].append("Aggressive/Energetic")
    if re.search(r"\?\s*[A-Z].*\?", all_text):  # Multiple questions
        characteristics["tone_indicators"].append("Inquisitive")
    if re.search(r"\.\.\.", all_text):  # Hesitation
        characteristics["tone_indicators"].append("Hesitant/Thoughtful")
    
    # Speech patterns
    if re.search(r"\b(lads?|boys?|men)\b", all_text):
        characteristics["speech_patterns"].append("Military/commanding")
    if re.search(r"\b(my|mine|I)\b", all_text):
        characteristics["speech_patterns"].append("Self-focused")
    
    return characteristics

def get_character_profile(speaker_name: str) -> dict:
    """Generate comprehensive character profile."""
    profile = {
        "name": speaker_name,
        "dialogue": [],
        "line_count": 0,
        "chapter1_lines": 0,
        "total_lines": 0,
        "characteristics": {},
        "audio_available": 0,
        "recommended_voice": None
    }
    
    # Get all dialogue lines
    try:
        with open(LINES_CSV, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            all_lines = [row for row in reader if row['Speaker'] == speaker_name]
            profile["total_lines"] = len(all_lines)
            profile["dialogue"] = [row['Text'] for row in all_lines[:10]]  # First 10 lines
    except FileNotFoundError:
        pass
    
    # Get Chapter 1 specific lines
    try:
        with open(CHAPTER1_CSV, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            ch1_lines = [row for row in reader if row['Speaker'] == speaker_name]
            profile["chapter1_lines"] = len(ch1_lines)
    except FileNotFoundError:
        pass
    
    # Analyze voice characteristics
    if profile["dialogue"]:
        profile["characteristics"] = analyze_dialogue_characteristics(profile["dialogue"])
    
    # Check for BG2 audio files
    search_patterns = [
        f"{speaker_name.upper()}*.WAV",
        f"{speaker_name.upper()[:6]}*.WAV",  # Truncated to 6 chars
    ]
    
    for pattern in search_patterns:
        matches = list(BG2_AUDIO.rglob(pattern))
        if matches:
            profile["audio_available"] = len(matches)
            break
    
    # Recommend similar companion voice if no audio
    if profile["audio_available"] == 0:
        profile["recommended_voice"] = recommend_voice_match(profile["characteristics"])
    
    return profile

def recommend_voice_match(characteristics: dict) -> str:
    """Recommend a companion voice based on characteristics."""
    recommendations = {
        "Scottish": "Korgan (dwarven berserker - gruff Scottish accent)",
        "Aggressive/Energetic": "Minsc (ranger - boisterous high energy)",
        "Theatrical": "HaerDalis (tiefling bard - poetic theatrical)",
        "Military/commanding": "Keldorn (paladin - noble commanding)",
        "Hesitant/Thoughtful": "Cernd (druid - philosophical contemplative)"
    }
    
    for indicator_type in ["accent_indicators", "tone_indicators"]:
        if characteristics.get(indicator_type):
            for indicator in characteristics[indicator_type]:
                if indicator in recommendations:
                    return recommendations[indicator]
    
    return "Use _default_ voice or closest companion match"

def print_character_profile(speaker_name: str):
    """Print formatted character profile."""
    profile = get_character_profile(speaker_name)
    
    print("=" * 70)
    print(f"CHARACTER PROFILE: {profile['name']}")
    print("=" * 70)
    
    print(f"\n📊 LINE COUNTS:")
    print(f"   • Chapter 1: {profile['chapter1_lines']} lines")
    print(f"   • Total game: {profile['total_lines']} lines")
    
    if profile['dialogue']:
        print(f"\n💬 SAMPLE DIALOGUE (first {len(profile['dialogue'])} lines):")
        for i, line in enumerate(profile['dialogue'][:5], 1):
            # Truncate long lines
            display_line = line[:80] + "..." if len(line) > 80 else line
            print(f"   {i}. \"{display_line}\"")
    
    print(f"\n🎤 VOICE CHARACTERISTICS:")
    chars = profile['characteristics']
    if chars.get('accent_indicators'):
        print(f"   • Accent: {', '.join(chars['accent_indicators'])}")
    if chars.get('tone_indicators'):
        print(f"   • Tone: {', '.join(chars['tone_indicators'])}")
    if chars.get('speech_patterns'):
        print(f"   • Patterns: {', '.join(chars['speech_patterns'])}")
    
    print(f"\n🎵 AUDIO AVAILABILITY:")
    if profile['audio_available'] > 0:
        print(f"   ✅ {profile['audio_available']} BG2 audio files found")
        print(f"   → Can build custom voice reference")
    else:
        print(f"   ❌ No BG2 audio files found")
        print(f"   → Recommended: {profile['recommended_voice']}")
    
    print("\n" + "=" * 70)

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python character_profile.py <SpeakerName>")
        print("\nExamples:")
        print("  python scripts/utils/character_profile.py Ilyich")
        print("  python scripts/utils/character_profile.py Yoshimo")
        print("  python scripts/utils/character_profile.py Jaheira")
        sys.exit(1)
    
    speaker_name = sys.argv[1]
    print_character_profile(speaker_name)

if __name__ == "__main__":
    main()
