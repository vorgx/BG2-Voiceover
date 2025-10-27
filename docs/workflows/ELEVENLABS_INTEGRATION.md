# ElevenLabs Integration Workflow

## Overview

This document describes the process of creating custom voices using ElevenLabs and integrating them into the BG2 Voiceover project. Used for characters without original BG2 audio.

## Current Usage

**Characters using ElevenLabs**:
- **Ilyich**: Duergar clan chief (v3, 30.9 seconds)

**Status**: Production ready, full integration complete

---

## Complete Workflow

### Phase 1: Character Analysis

#### Step 1: Run Character Profile Generator

```powershell
cd "C:\Users\tenod\source\repos\BG2 Voiceover"
python scripts/utils/character_profile.py --speaker Ilyich --input data/chapter1_split.csv
```

**Output Example**:
```
Character Profile: Ilyich
========================
Total lines: 4
Average line length: 45 characters

Sample dialogue:
- "Be alert, laddies! Stop you!"
- "This place is your doom, and you're all dead men!"
- "Come and get 'em!"
- "No mercy!"

Analysis:
------------------------
Accent: Scottish
Tone: Aggressive, commanding
Speech Pattern: Short, direct, imperative
Energy: High
Personality: Military leader, hostile

Voice Attributes:
- Gruff timbre
- Deep pitch
- Commanding presence
- Hostile/aggressive

Recommended Voice Tags for ElevenLabs:
- scottish accent
- military commander
- aggressive
- gruff
- deep voice
- hostile tone
- commanding
```

#### Step 2: Create ElevenLabs Prompt

Based on character profile, craft a prompt:

```
Create a voice for a Scottish military commander character. Male, 
aggressive and hostile tone, deep gruff voice. This is a duergar 
(evil dwarf) dungeon leader who commands troops. Voice should sound 
threatening and authoritative with a distinct Scottish accent. 
Examples of dialogue: "No mercy!", "Come and get 'em!", 
"This place is your doom!"
```

### Phase 2: ElevenLabs Voice Generation

#### Step 1: Access ElevenLabs Voice Lab

1. Go to https://elevenlabs.io
2. Navigate to Voice Lab
3. Click "Create Voice"

#### Step 2: Configure Voice Settings

**Option A: Voice Design (Recommended)**
- Enter character prompt
- Adjust sliders:
  - Age: Middle-aged to older
  - Gender: Male
  - Accent: Scottish (strong)
  - Tone: Aggressive
- Generate samples, iterate until satisfied

**Option B: Instant Voice Cloning**
- Upload audio samples if available
- Requires 1+ minute of clean speech
- Less control but faster

#### Step 3: Generate and Download

1. Once satisfied, save voice profile
2. Generate sample audio with test line:
   ```
   "This place is your doom, and you're all dead men!"
   ```
3. Download as MP3 (highest quality)
4. Save to: `BG2 Files/Character Samples from Elevenlabs/[character].mp3`

**File naming convention**: `[character] v[version].mp3`
- Example: `ilyic v3.mp3` (note: typo in actual filename, kept for consistency)

### Phase 3: Integration into Project

#### Step 1: Create Reference Builder Script

If not exists, create `scripts/utils/build_[character]_ref.py`:

```python
"""
Build [Character] voice reference from ElevenLabs generated audio.
"""
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ELEVENLABS_SOURCE = ROOT / "BG2 Files" / "Character Samples from Elevenlabs" / "[character] v1.mp3"
OUTPUT = ROOT / "refs" / "[character]_ref.wav"

def convert_mp3_to_wav(mp3_path: Path, wav_path: Path) -> None:
    """Convert MP3 to WAV format using librosa"""
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
    print("🎤 Building [Character] Voice Reference")
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
    print(f"\n✅ [Character] reference ready at: refs/[character]_ref.wav")

if __name__ == "__main__":
    main()
```

#### Step 2: Run Reference Builder

```powershell
python scripts/utils/build_[character]_ref.py
```

**Expected Output**:
```
🎤 Building [Character] Voice Reference
   Using ElevenLabs generated audio

   ✓ Found: [character] v1.mp3
   Converting MP3 to WAV...
   Duration: 25.5 seconds

✅ [Character] reference ready at: refs/[character]_ref.wav
```

#### Step 3: Update voices.json

Add entry to `data/voices.json`:

```json
{
  "[Character]": {
    "ref": "refs/[character]_ref.wav",
    "preset": "male_gruff",  // or appropriate preset
    "notes": "ElevenLabs custom voice generation, [description]",
    "status": "Ready for testing"
  }
}
```

**Optional**: Add post-processing parameters:
```json
{
  "[Character]": {
    "ref": "refs/[character]_ref.wav",
    "preset": "male_gruff",
    "pitch_shift": -2,           // Make deeper
    "speed": 0.95,               // Slow down 5%
    "interval_silence": 0.4,     // Longer pauses
    "notes": "ElevenLabs custom voice v1, with post-processing",
    "status": "Ready for testing"
  }
}
```

### Phase 4: Testing and Iteration

#### Step 1: Generate Test Lines

Create test CSV with 3-5 representative lines:

```csv
StrRef,Speaker,Text
12345,[Character],Short line example.
12346,[Character],Medium length line with more words and expression!
12347,[Character],Very long line with complex sentence structure, multiple clauses, and varied punctuation... what happens?
```

#### Step 2: Synthesize Test Lines

```powershell
C:\Users\tenod\source\repos\TTS\index-tts\.venv\Scripts\python.exe scripts\core\synth.py --input data\test_[character].csv
```

#### Step 3: Evaluate Quality

Listen for:
- **Accent accuracy**: Does it match character profile?
- **Tone consistency**: Appropriate emotion/attitude?
- **Voice timbre**: Matches character description?
- **Quality**: Clean audio, no artifacts?
- **Naturalness**: Sounds like a real person?

#### Step 4: Iterate if Needed

**If voice needs improvement**:

1. **Return to ElevenLabs**:
   - Adjust voice settings
   - Try different prompts
   - Generate new version
   - Download as `[character] v2.mp3`

2. **Update reference builder**:
   ```python
   ELEVENLABS_SOURCE = ROOT / "BG2 Files" / "Character Samples from Elevenlabs" / "[character] v2.mp3"
   ```

3. **Rebuild reference and retest**

**If voice is good but needs tweaks**:
- Add/adjust post-processing in `voices.json`
- Test different pitch_shift values
- Test different speed values
- Add emotion detection if needed

#### Step 5: Lock Voice

Once satisfied:
```json
{
  "[Character]": {
    "ref": "refs/[character]_ref.wav",
    "preset": "male_gruff",
    "pitch_shift": -2,
    "speed": 0.95,
    "notes": "ElevenLabs custom voice v2, approved",
    "status": "Locked"  // ← Change to Locked
  }
}
```

---

## Ilyich Case Study

### Version History

#### v1 (Initial)
- **Duration**: ~19 seconds
- **Prompt**: Basic Scottish aggressive voice
- **Issue**: Not deep enough, needed more menace
- **Action**: Regenerated in ElevenLabs

#### v2 (Improved)
- **Duration**: 26 seconds
- **Prompt**: Enhanced with "deep voice", "hostile tone"
- **Issue**: Still needed more depth and slower pacing
- **Action**: Added post-processing

#### v3 (Final)
- **Duration**: 30.9 seconds
- **Prompt**: Final iteration with optimal settings
- **Post-processing**:
  - pitch_shift: -2 (subtle deepening)
  - speed: 0.95 (5% slower for deliberate delivery)
  - interval_silence: 0.45 (dramatic pauses)
- **Emotion**: 30% Angry, 15% Disgusted (auto-detected)
- **Status**: ✅ Approved, locked

### Lessons Learned

1. **Iteration is key**: Don't settle on first version
2. **Start with good base**: Get voice close in ElevenLabs first
3. **Post-processing helps**: But can't fix fundamental mismatches
4. **Test with actual dialogue**: Character profile samples essential
5. **Combine techniques**: Voice + post-processing + emotion = best results

---

## ElevenLabs Best Practices

### Voice Quality Tips

1. **Prompt Clarity**:
   - Be specific about accent, age, gender
   - Include character context (role, personality)
   - Provide example dialogue
   - Mention timbre/pitch preferences

2. **Sample Quality**:
   - Use highest quality download (MP3 320kbps)
   - Ensure 20-60 seconds length (optimal for Index-TTS)
   - Avoid background noise or music
   - Get varied speech (different emotions, speeds)

3. **Testing**:
   - Test multiple versions before committing
   - Compare with similar characters
   - Get feedback from others
   - Test across different line types

### Cost Considerations

**ElevenLabs Pricing** (as of 2025):
- Free tier: Limited voice generations
- Pro tier: More generations, higher quality
- Enterprise: Unlimited, commercial use

**Recommendations**:
- Use free tier for initial experiments
- Upgrade for production voices
- Generate longer samples (saves regenerations)
- Save all versions for comparison

### When to Use ElevenLabs

**Good candidates**:
- ✅ No original BG2 audio available
- ✅ Character has significant dialogue (10+ lines)
- ✅ Need specific accent/voice type
- ✅ Character is unique/important to story

**Not recommended**:
- ❌ Minor characters (1-2 lines) - use borrowed voices instead
- ❌ Generic NPCs - use existing references
- ❌ When good BG2 audio exists - always prefer original

---

## Technical Details

### MP3 to WAV Conversion

**Method 1: pydub (Preferred)**
```python
from pydub import AudioSegment
audio = AudioSegment.from_mp3(str(mp3_path))
audio.export(str(wav_path), format="wav")
```

**Method 2: librosa (Fallback)**
```python
import librosa
import soundfile as sf
audio, sr = librosa.load(str(mp3_path), sr=None)
sf.write(str(wav_path), audio, sr)
```

**Output format**:
- Sample rate: Preserves original (usually 44.1kHz)
- Channels: Mono (Index-TTS requirement)
- Bit depth: 16-bit PCM
- Format: WAV (uncompressed)

### File Size Expectations

| Duration | MP3 (320kbps) | WAV (16-bit) |
|----------|---------------|--------------|
| 10s      | ~400 KB       | ~800 KB      |
| 20s      | ~800 KB       | ~1.6 MB      |
| 30s      | ~1.2 MB       | ~2.4 MB      |
| 60s      | ~2.4 MB       | ~4.8 MB      |

**Recommendation**: Keep references 20-60 seconds for balance of quality and file size.

### Index-TTS Compatibility

- ✅ Accepts WAV references of any length
- ✅ Longer references often produce better quality
- ✅ Can extract voice characteristics from varied samples
- ⚠️ Very short references (<10s) may lack variety
- ⚠️ Very long references (>120s) provide diminishing returns

---

## Troubleshooting

### Issue: MP3 conversion fails
**Error**: `ModuleNotFoundError: No module named 'pydub'`
**Fix**: Install pydub or fallback to librosa automatically handles this

### Issue: Voice doesn't match accent
**Cause**: ElevenLabs prompt not specific enough
**Fix**: 
1. Be more explicit in prompt
2. Use accent examples in generation
3. Try different base voices in ElevenLabs

### Issue: Voice sounds robotic
**Cause**: Sample too short or monotone
**Fix**:
1. Generate longer sample (30+ seconds)
2. Include varied emotion in sample
3. Use more expressive base voice

### Issue: Inconsistent quality across lines
**Cause**: Reference sample has quality variations
**Fix**:
1. Ensure ElevenLabs sample is consistent
2. Regenerate sample if needed
3. Check for background noise or artifacts

---

## Future Enhancements

### Planned:
1. **Batch voice generation**: Generate multiple characters at once
2. **Voice variation**: Multiple samples per character for variety
3. **Quality presets**: "fast", "standard", "high quality" workflows
4. **Integration with Voice Lab API**: Automated voice generation

### Experimental:
- **Voice morphing**: Blend multiple ElevenLabs voices
- **Dynamic voice selection**: Choose voice based on emotion/context
- **Local voice cloning**: Self-hosted alternative to ElevenLabs

---

## Comparison: ElevenLabs vs. Original Audio

### ElevenLabs Advantages:
- ✅ Can create any voice type
- ✅ Consistent quality across all lines
- ✅ Customizable (accent, tone, characteristics)
- ✅ Clean audio (no game noise)
- ✅ Modern voice quality

### Original Audio Advantages:
- ✅ Authentic to character
- ✅ Matches existing fan expectations
- ✅ Professional voice actor performance
- ✅ Free (already available)
- ✅ No generation needed

### Hybrid Approach (Current Strategy):
- Use original audio when available (7/8 Chapter 1 speakers)
- Use ElevenLabs for unique voices without audio (Ilyich)
- Apply post-processing to blend both sources
- Result: Consistent quality across all characters

---

*Last Updated: October 27, 2025*
*Status: Production Ready, Proven with Ilyich*
