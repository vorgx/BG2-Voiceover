# Emotion System Documentation

## Overview

The BG2 Voiceover project uses **emotion vectors** (Index-TTS v2.0 feature) to add emotional nuance to synthesized dialogue. This system is currently **selectively enabled** for specific characters requiring emotional depth.

## Current Status (October 27, 2025)

- **Enabled for**: Ilyich only
- **Disabled for**: All other speakers (Jaheira, Minsc, Imoen, Yoshimo, Valygar, Rielev, Dryad)
- **Emotion Cap**: 30% maximum intensity (0.3 on 0.0-1.0 scale)
- **Implementation**: `src/bg2vo/emotions.py` + `scripts/core/synth.py`

## Emotion Vector Format

Emotion vectors are **8-dimensional arrays** controlling emotional expression:

```python
[Happy, Angry, Sad, Afraid, Disgusted, Melancholic, Surprised, Calm]
```

Each dimension accepts values from **0.0 (none) to 1.0 (maximum)**.

### Current Emotion Presets

```python
emotion_vectors = {
    "angry": {
        "vector": [0.0, 0.3, 0.0, 0.0, 0.15, 0.0, 0.0, 0.0],  
        # 30% Angry, 15% Disgusted
    },
    "sad": {
        "vector": [0.0, 0.0, 0.3, 0.0, 0.0, 0.2, 0.0, 0.0],  
        # 30% Sad, 20% Melancholic
    },
    "happy": {
        "vector": [0.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.15, 0.0],  
        # 30% Happy, 15% Surprised
    },
    "fear": {
        "vector": [0.0, 0.0, 0.0, 0.3, 0.0, 0.0, 0.15, 0.0],  
        # 30% Afraid, 15% Surprised
    },
    "urgent": {
        "vector": [0.0, 0.25, 0.0, 0.15, 0.0, 0.0, 0.0, 0.0],  
        # 25% Angry, 15% Afraid
    },
    "hesitant": {
        "vector": [0.0, 0.0, 0.2, 0.2, 0.0, 0.0, 0.0, 0.0],  
        # 20% Sad, 20% Afraid
    },
    "neutral": {
        "vector": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3],  
        # 30% Calm
    },
}
```

## Emotion Detection Algorithm

Located in `src/bg2vo/emotions.py`, function `detect_emotion(text: str) -> EmotionType`

### Detection Rules

1. **Angry** Detection:
   - Keywords: "kill", "die", "death", "fight", "attack", "crush", "destroy", "no mercy", "doom", "dead", "blood"
   - Pattern: Multiple `!` (3+)
   - Priority: High (checked first)

2. **Sad** Detection:
   - Keywords: "sorry", "regret", "loss", "grief", "mourn", "cry", "weep", "farewell", "goodbye"
   - Pattern: `...` (trailing ellipsis)

3. **Fear** Detection:
   - Keywords: "afraid", "fear", "terror", "run", "escape", "help", "danger", "monster"
   - Pattern: Multiple `?!`

4. **Happy** Detection:
   - Keywords: "thank", "wonderful", "excellent", "great", "joy", "laugh", "smile", "celebration"
   - Pattern: Multiple `!` with happy keywords

5. **Urgent** Detection:
   - Keywords: "quick", "hurry", "now", "fast", "immediately", "urgent", "run"
   - Pattern: Short sentences with `!`

6. **Hesitant** Detection:
   - Keywords: "maybe", "perhaps", "unsure", "don't know", "hesitate"
   - Pattern: Multiple `...`

7. **Default**: "neutral" if no patterns match

### Example Detection

```python
detect_emotion("No mercy!") → "angry"
detect_emotion("I'm so sorry for your loss...") → "sad"
detect_emotion("Quick! We must escape!") → "urgent"
detect_emotion("Hello, traveler.") → "neutral"
```

## Integration in Synthesis Pipeline

### Location: `scripts/core/synth.py`, lines 154-165

```python
# EMOTION DETECTION: Use manual emotion if provided, auto-detect for Ilyich only
if manual_emotion and manual_emotion.strip():
    emotion = manual_emotion.strip().lower()
    print(f"  🎭 Manual emotion: {emotion}")
    emotion_config = get_emotion_config(emotion, speaker)
elif speaker.lower() == "ilyich":
    # Auto-detect emotion for Ilyich to make him more aggressive
    emotion = detect_emotion(text)
    print(f"  🎭 Auto-detected emotion for Ilyich: {emotion}")
    emotion_config = get_emotion_config(emotion, speaker)
else:
    # Skip auto-detection for other speakers
    emotion_config = None
```

### Key Points:
1. **Manual emotion** takes precedence (from CSV "Emotion" column)
2. **Auto-detection** only fires for `speaker.lower() == "ilyich"`
3. **All other speakers** bypass emotion system (use base voice only)
4. Emotion config merged into voice config before synthesis

## Why 30% Cap?

### History:
- **Initial testing**: 100% emotion (1.0) caused severe artifacts:
  - Unwanted laughter
  - Over-acting
  - Distorted audio
  - Loss of character voice consistency

- **50% cap**: Still too strong, noticeable artifacting

- **30% cap**: ✅ Sweet spot
  - Subtle emotional influence
  - Maintains voice quality
  - Natural-sounding result
  - No artifacts

### Tuning Guidelines:
- **0-20%**: Very subtle, barely noticeable
- **20-30%**: ✅ Balanced, natural emotion
- **30-50%**: Strong emotion, risk of artifacts
- **50-100%**: ❌ High artifact risk, over-acting

## Extending to Other Characters

To enable emotion detection for additional speakers:

### Option 1: Add to Auto-Detection List
```python
# In scripts/core/synth.py, line 156
elif speaker.lower() in ["ilyich", "sarevok", "bodhi"]:  # Add speakers here
    emotion = detect_emotion(text)
    emotion_config = get_emotion_config(emotion, speaker)
```

### Option 2: Manual Emotion Column in CSV
Add "Emotion" column to input CSV:
```csv
StrRef,Speaker,Text,Emotion
12345,Sarevok,You will suffer.,angry
12346,Bodhi,How delicious...,neutral
```

System will use manual emotion for those lines.

## Emotion vs. Audio Reference Method

### Old Method (Disabled):
- Used emotion audio clips: `refs/emotions/ilyich/angry.wav`
- Required separate audio files for each emotion
- Blended with `emo_alpha` parameter (0.0-1.0)
- **Problem**: Hard to source quality emotion clips

### Current Method (Emotion Vectors):
- Mathematical vectors (no audio files needed)
- Precise control over emotion dimensions
- **Advantage**: No additional audio required
- **Advantage**: Easy to tune and iterate
- **Advantage**: Consistent across all lines

## API Mode Requirement

Emotion vectors require **Index-TTS API mode** (not CLI):

```python
# Triggers API mode
use_api = any(k in config_dict for k in ["emo_vector", "interval_silence", ...])

if use_api:
    synth_with_api(...)  # API mode with emotion support
else:
    # CLI mode (no emotion)
```

API mode generates temporary Python script, runs in Index-TTS environment.

## Performance Impact

- **Generation time**: +5-10% slower than base synthesis (negligible)
- **Quality**: No degradation when capped at 30%
- **CUDA GPU**: Fully compatible, maintains ~10x speedup

## Future Enhancements

### Planned:
1. **Context-aware detection**: Consider dialogue history
2. **Character personality profiles**: Different emotion baselines per character
3. **Intensity scaling**: Dynamic cap based on character type
4. **Multi-emotion blending**: Combine multiple emotions (e.g., 20% angry + 10% sad)

### Experimental:
- **Emotion interpolation**: Smooth transitions between emotions in long dialogue
- **Scene-based emotions**: Apply emotions based on game state/location
- **Dynamic caps**: Adjust max intensity per emotion type

## Testing Recommendations

When adding emotion to new characters:

1. **Start conservative**: Begin with 20% cap, test
2. **Test extreme lines**: Find lines with strong emotions, verify no artifacts
3. **Compare with base**: Generate with/without emotion, ensure improvement
4. **Check consistency**: Verify voice remains recognizable across emotions
5. **User feedback**: Have multiple people listen and provide input

## Technical Notes

### Emotion Vector Validation
- Vectors must be exactly 8 elements
- Each element must be 0.0-1.0
- System does NOT normalize (manual control required)
- None values allowed (bypasses emotion)

### Debugging
Enable emotion debug output:
```python
if emotion_config:
    print(f"  🎭 Using emotion: {emotion}")
    print(f"  🎭 Vector: {emotion_config.get('emo_vector')}")
```

### Known Limitations
- Cannot detect sarcasm (tone vs. content conflict)
- Struggles with mixed emotions in single line
- Language-specific (English keywords only)
- No context beyond current line

---

*Last Updated: October 27, 2025*
*Status: Production Ready (Ilyich), Extensible for Future Characters*
