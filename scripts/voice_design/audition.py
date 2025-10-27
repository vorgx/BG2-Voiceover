"""
Voice Audition Tool

Generate 2-3 voice variants for a character and compare quality.
Helps choose the best voice before committing to full synthesis.
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHARACTERS_CSV = ROOT / "data" / "characters.csv"
VOICES_JSON = ROOT / "data" / "voices.json"
AUDITIONS_DIR = ROOT / "auditions"
AUDITIONS_DIR.mkdir(exist_ok=True)

# Index-TTS setup
INDEX_TTS_ROOT = Path(r"C:\Users\tenod\source\repos\TTS\index-tts")
INDEX_TTS_BIN = str(INDEX_TTS_ROOT / ".venv" / "Scripts" / "indextts.exe")
CONFIG = str(INDEX_TTS_ROOT / "checkpoints" / "config.yaml")

# Sample test phrases (varied emotional content)
TEST_PHRASES = {
    "neutral": "I understand. We should proceed with caution.",
    "happy": "Excellent! This is exactly what we needed to find.",
    "angry": "That's the last time I'll tolerate such behavior!",
    "sad": "I... I'm not sure I can go on like this anymore.",
    "commanding": "Everyone, listen carefully. Here's what we're going to do."
}

# Preset suggestions by archetype
PRESET_SUGGESTIONS = {
    # Female
    ("F", "Cheery"): ["female_bright", "female_light", "female_uplift"],
    ("F", "Stern"): ["female_mature", "female_strong", "female_flat"],
    ("F", "Sardonic"): ["female_cool", "female_mature", "female_sardonic"],
    ("F", "Timid"): ["female_gentle", "female_light", "female_soft"],
    ("F", "Idealist"): ["female_uplift", "female_bright", "female_gentle"],
    
    # Male
    ("M", "Boisterous"): ["male_booming", "male_strong", "male_heroic"],
    ("M", "Arrogant"): ["male_sardonic", "male_cool", "male_smooth"],
    ("M", "Stoic"): ["male_flat", "male_deep", "male_wise"],
    ("M", "Charming"): ["male_smooth", "male_theatrical", "male_noble"],
    ("M", "Menacing"): ["male_deep", "male_menacing", "male_dark"],
    ("M", "Righteous"): ["male_noble", "male_wise", "male_heroic"],
}

def load_character(name):
    """Load character info from characters.csv"""
    with open(CHARACTERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Canonical'].lower() == name.lower():
                return row
    return None

def get_preset_suggestions(character):
    """Get 3 preset suggestions based on character traits"""
    gender = character['Gender']
    archetype = character['Archetype']
    
    # Try exact match
    key = (gender, archetype)
    if key in PRESET_SUGGESTIONS:
        return PRESET_SUGGESTIONS[key][:3]
    
    # Fallback generic suggestions
    if gender == "F":
        return ["female_bright", "female_mature", "female_cool"]
    else:
        return ["male_booming", "male_sardonic", "male_flat"]

def synthesize_variant(character_name, variant_num, voice_config, phrase_type, text):
    """Generate one audio variant"""
    output_file = AUDITIONS_DIR / f"{character_name}_{variant_num}_{phrase_type}.wav"
    
    if output_file.exists():
        return output_file  # Skip if already exists
    
    # Determine voice reference or preset
    if isinstance(voice_config, dict):
        voice_ref = voice_config.get("ref") or voice_config.get("voice", "narrator")
    else:
        voice_ref = voice_config
    
    args = [
        INDEX_TTS_BIN,
        "-c", CONFIG,
        "-v", voice_ref,
        "-o", str(output_file),
        "-f",  # Force overwrite
        text
    ]
    
    print(f"   Generating: {output_file.name}")
    result = subprocess.run(args, cwd=INDEX_TTS_ROOT, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"   ⚠️  Warning: Failed to generate {output_file.name}")
        return None
    
    return output_file

def create_audition_report(character, variants, phrase_types):
    """Create HTML report for comparing variants"""
    report_file = AUDITIONS_DIR / f"{character['Canonical']}_audition.html"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Voice Audition: {character['Canonical']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        .character-info {{ background: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .variant {{ background: white; padding: 15px; margin-bottom: 15px; border-radius: 5px; border-left: 4px solid #4CAF50; }}
        .phrase {{ margin: 10px 0; padding: 10px; background: #f9f9f9; border-radius: 3px; }}
        audio {{ width: 100%; max-width: 500px; }}
        .vote {{ margin-top: 15px; }}
        button {{ padding: 10px 20px; margin: 5px; cursor: pointer; background: #4CAF50; color: white; border: none; border-radius: 3px; }}
        button:hover {{ background: #45a049; }}
        .info-grid {{ display: grid; grid-template-columns: 150px 1fr; gap: 5px; }}
        .info-label {{ font-weight: bold; }}
    </style>
</head>
<body>
    <h1>🎤 Voice Audition: {character['Canonical']}</h1>
    
    <div class="character-info">
        <h2>Character Profile</h2>
        <div class="info-grid">
            <div class="info-label">Gender:</div><div>{character['Gender']}</div>
            <div class="info-label">Age:</div><div>{character['AgeBand']}</div>
            <div class="info-label">Archetype:</div><div>{character['Archetype']}</div>
            <div class="info-label">Energy:</div><div>{character['Energy']}</div>
            <div class="info-label">Timbre:</div><div>{character['Timbre']}</div>
            <div class="info-label">Accent:</div><div>{character['Accent']}</div>
            <div class="info-label">Notes:</div><div>{character['Notes']}</div>
        </div>
    </div>
    
    <h2>Compare Variants</h2>
"""
    
    for i, (variant_name, config) in enumerate(variants, 1):
        html += f"""
    <div class="variant">
        <h3>Variant {i}: {variant_name}</h3>
"""
        
        for phrase_type in phrase_types:
            audio_file = f"{character['Canonical']}_{i}_{phrase_type}.wav"
            text = TEST_PHRASES[phrase_type]
            
            html += f"""
        <div class="phrase">
            <strong>{phrase_type.title()}:</strong> "{text}"<br>
            <audio controls src="{audio_file}"></audio>
        </div>
"""
        
        html += """
        <div class="vote">
            <button onclick="alert('Mark this variant in characters.csv!')">✓ Choose This Voice</button>
        </div>
    </div>
"""
    
    html += """
    <h2>Next Steps</h2>
    <ol>
        <li>Listen to all variants across different emotional contexts</li>
        <li>Choose the variant that best matches the character</li>
        <li>Update characters.csv with chosen preset/reference</li>
        <li>Update voices.json with final configuration</li>
        <li>Mark character as "Auditioned" status</li>
    </ol>
    
</body>
</html>
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return report_file

def run_audition(character_name, phrase_types=None):
    """Run complete audition for a character"""
    print("=" * 70)
    print(f"VOICE AUDITION: {character_name}")
    print("=" * 70)
    print()
    
    # Load character
    char = load_character(character_name)
    if not char:
        print(f"❌ Character '{character_name}' not found in characters.csv")
        return
    
    print(f"Character: {char['Canonical']}")
    print(f"Profile: {char['Gender']}/{char['AgeBand']}/{char['Archetype']} - {char['Energy']} energy")
    print()
    
    # Check if already has reference
    if char['RefFile']:
        print(f"ℹ️  Character already has reference: {char['RefFile']}")
        print("   Using reference + suggested presets for comparison")
        print()
    
    # Get variants to test
    variants = []
    
    # Variant 1: Current preset (if any)
    if char['VoicePreset']:
        variants.append(("Current Preset", char['VoicePreset']))
    
    # Variant 2-4: Suggested presets
    suggestions = get_preset_suggestions(char)
    for i, preset in enumerate(suggestions):
        if not char['VoicePreset'] or preset != char['VoicePreset']:
            variants.append((f"Suggested {preset}", preset))
            if len(variants) >= 3:
                break
    
    # Variant with reference (if exists)
    if char['RefFile']:
        ref_path = str(ROOT / char['RefFile'])
        if Path(ref_path).exists():
            variants.append(("Multi-Reference", {"ref": ref_path}))
    
    # Limit to 3 variants
    variants = variants[:3]
    
    print(f"📋 Testing {len(variants)} variants:")
    for i, (name, _) in enumerate(variants, 1):
        print(f"   {i}. {name}")
    print()
    
    # Select phrases
    if phrase_types is None:
        phrase_types = ["neutral", "happy", "angry"]  # Default 3 phrases
    
    print(f"🎵 Generating audio for {len(phrase_types)} test phrases...")
    print()
    
    # Generate all variants
    for i, (variant_name, config) in enumerate(variants, 1):
        print(f"Variant {i}: {variant_name}")
        for phrase_type in phrase_types:
            text = TEST_PHRASES[phrase_type]
            synthesize_variant(char['Canonical'], i, config, phrase_type, text)
        print()
    
    # Create comparison report
    print("📄 Creating comparison report...")
    report = create_audition_report(char, variants, phrase_types)
    print(f"   ✓ {report}")
    print()
    
    # Open report
    print("🌐 Opening audition report in browser...")
    subprocess.run(["cmd", "/c", "start", str(report)], shell=True)
    
    print()
    print("=" * 70)
    print("✅ AUDITION COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Listen to all variants in the browser")
    print("  2. Choose the best voice")
    print(f"  3. python scripts/character_lib.py update {char['Canonical']} Auditioned")
    print("  4. Update voices.json with chosen configuration")
    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/audition.py CHARACTER")
        print("  python scripts/audition.py CHARACTER neutral happy angry sad")
        print()
        print("Examples:")
        print("  python scripts/audition.py Minsc")
        print("  python scripts/audition.py Jaheira neutral angry commanding")
        sys.exit(1)
    
    character = sys.argv[1]
    phrases = sys.argv[2:] if len(sys.argv) > 2 else None
    
    # Validate phrases
    if phrases:
        invalid = [p for p in phrases if p not in TEST_PHRASES]
        if invalid:
            print(f"❌ Invalid phrase types: {', '.join(invalid)}")
            print(f"Valid options: {', '.join(TEST_PHRASES.keys())}")
            sys.exit(1)
    
    run_audition(character, phrases)
