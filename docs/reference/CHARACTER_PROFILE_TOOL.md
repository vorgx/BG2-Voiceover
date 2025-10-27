# Character Profile Tool

Automatically generates character profiles including dialogue samples, voice characteristics, and audio availability.

## Usage

```powershell
python scripts/utils/character_profile.py <CharacterName>
```

## Examples

```powershell
# Get profile for Ilyich
python scripts/utils/character_profile.py Ilyich

# Get profile for any character
python scripts/utils/character_profile.py Yoshimo
python scripts/utils/character_profile.py Jaheira
python scripts/utils/character_profile.py Valygar
```

## What It Shows

### 📊 Line Counts
- Chapter 1 lines (for current chapter work)
- Total game lines (full scope)

### 💬 Sample Dialogue
- First 5-10 dialogue lines
- Helps understand character personality and speech patterns

### 🎤 Voice Characteristics
**Automatically detected:**
- **Accent indicators**: Scottish, Theatrical, Upper-class, Archaic/Formal
  - Detected from dialect patterns: "laddie", "ye", "'tis", "indeed", etc.
  
- **Tone indicators**: Aggressive/Energetic, Inquisitive, Hesitant/Thoughtful
  - Based on punctuation and sentence structure
  
- **Speech patterns**: Military/commanding, Self-focused
  - Based on word choices and phrasing

### 🎵 Audio Availability
- Searches for BG2 audio files matching the character
- If found: Shows count and confirms reference can be built
- If not found: Recommends similar companion voice

## Voice Recommendations

When no audio is available, the tool suggests companions with similar characteristics:

| Characteristic | Recommended Voice |
|---------------|-------------------|
| Scottish accent | Korgan (dwarven berserker) |
| Aggressive/Energetic | Minsc (ranger) |
| Theatrical | HaerDalis (tiefling bard) |
| Military/commanding | Keldorn (paladin) |
| Hesitant/Thoughtful | Cernd (druid) |

### Using Borrowed Voices

When using another companion's voice, configure with differentiation in `voices.json`:

```json
{
  "CharacterName": {
    "ref": "refs/borrowed_character_ref.wav",
    "preset": "appropriate_preset",
    "notes": "Description (borrowed from SourceCharacter)",
    "emotion": "borrowed_voice",
    "speed": 0.95,
    "pitch_shift": -2,
    "status": "Locked"
  }
}
```

- **emotion**: `"borrowed_voice"` marker tracks which characters use adapted companion voices
- **speed**: Slightly slower (0.95) or faster (1.05) to differentiate from original
- **pitch_shift**: Shift semitones up (+2) or down (-2) for vocal distinction

## Example Output

```
======================================================================
CHARACTER PROFILE: Ilyich
======================================================================

📊 LINE COUNTS:
   • Chapter 1: 4 lines
   • Total game: 4 lines

💬 SAMPLE DIALOGUE (first 4 lines):
   1. "Be alert, laddies! We've got company. Ho, prisoners!..."
   2. "Suffice to say, this place is your doom..."
   3. "I won't be givin' 'em to you. Come and get 'em..."
   4. "At 'em, lads! No mercy!"

🎤 VOICE CHARACTERISTICS:
   • Accent: Scottish
   • Tone: Aggressive/Energetic
   • Patterns: Military/commanding

🎵 AUDIO AVAILABILITY:
   ❌ No BG2 audio files found
   → Recommended: Korgan (dwarven berserker - gruff Scottish accent)
```

## Workflow Integration

### Before Creating Voice References

1. Run character profile to understand the character
2. Check if BG2 audio is available
3. If yes: Build custom reference from their audio
4. If no: Use recommended companion voice

### Example Workflow

```powershell
# Step 1: Get character info
python scripts/utils/character_profile.py Ilyich

# Step 2: Based on output, if audio available:
python scripts/utils/build_<character>_ref.py

# Step 3: If no audio, use recommended voice in voices.json
# Recommendation: "Korgan" → Use Korgan's reference
```

## Adding to Future Chapters

When working on new chapters:

```powershell
# Quickly profile all speakers in a chapter
python -c "import csv; speakers = set(r['Speaker'] for r in csv.DictReader(open('data/chapter2_lines.csv', encoding='utf-8'))); [print(s) for s in sorted(speakers)]"

# Then profile each one
python scripts/utils/character_profile.py <SpeakerName>
```

## Technical Details

### Data Sources
- `data/lines.csv` - Full game dialogue
- `data/chapter1_lines.csv` - Chapter-specific lines
- `BG2 Files/` - Original audio files

### Accent Detection Patterns
- **Scottish**: laddie, 'is, givin', th', ye, 'em
- **Theatrical**: dost, thou, thee, forsooth, 'tis
- **Upper-class**: indeed, quite, rather, certainly
- **Archaic/Formal**: shall, thee, thy, doth

### Tone Detection
- **Aggressive**: Multiple exclamation marks
- **Inquisitive**: Multiple questions
- **Hesitant**: Ellipsis (...) usage

### Speech Patterns
- **Military**: Uses "lads", "boys", "men"
- **Self-focused**: Frequent "I", "my", "mine"
