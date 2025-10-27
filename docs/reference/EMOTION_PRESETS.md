# Enhanced voices.json Structure with Emotion Presets

This document describes the enhanced `voices.json` structure for supporting emotion-driven vocalization synthesis.

## Structure

```json
{
  "Character Name": {
    "ref": "refs/character_ref.wav",
    "preset": "preset_name",
    "notes": "Character description",
    "status": "Locked/Pending/Draft",
    
    // NEW: Emotion presets for vocalizations
    "emotion_presets": {
      "grunt": {
        "emo_audio_prompt": "refs/emotions/character/grunt_12345.wav",
        "emo_text": "pained frustrated grunt",
        "emo_alpha": 0.8
      },
      "yell": {
        "emo_audio_prompt": "refs/emotions/character/yell_23456.wav",
        "emo_text": "angry determined yell",
        "emo_alpha": 0.7
      },
      "cry": {
        "emo_audio_prompt": "refs/emotions/character/cry_34567.wav",
        "emo_text": "grief stricken sobbing",
        "emo_alpha": 0.9
      },
      "laugh": {
        "emo_audio_prompt": "refs/emotions/character/laugh_45678.wav",
        "emo_text": "nervous awkward chuckle",
        "emo_alpha": 0.6
      },
      // Add other emotion types as needed
      // Supported: grunt, scream, moan, yell, gasp, laugh, cry, cough, sigh, generic
    }
  }
}
```

## Emotion Preset Fields

### `emo_audio_prompt` (required)
Path to reference audio file exhibiting the emotion. This should be:
- Original game audio clip showing the character expressing this emotion
- 1-5 seconds long (longer is better for emotion capture)
- Clear emotion expression (e.g., actual grunt, yell, cry from game)

### `emo_text` (optional)
Text description of the emotion to guide synthesis. Examples:
- "pained frustrated grunt"
- "angry determined yell"
- "grief stricken sobbing"
- "nervous awkward chuckle"
- "battle fury roar"

### `emo_alpha` (optional, default: 0.5)
Strength of emotion influence (0.0-1.0):
- **0.0-0.3**: Subtle emotion hint
- **0.4-0.6**: Moderate emotion influence (default)
- **0.7-0.9**: Strong emotion dominance
- **1.0**: Pure emotion (may lose intelligibility)

**Recommended values by vocalization type:**
- Grunt: 0.7-0.9 (strong physical expression)
- Yell: 0.6-0.8 (maintain some articulation)
- Cry: 0.8-0.95 (heavy emotion)
- Laugh: 0.5-0.7 (keep natural rhythm)
- Gasp: 0.7-0.9 (sharp physical reaction)
- Cough: 0.8-1.0 (very physical)
- Sigh: 0.5-0.7 (subtle expression)

## Fallback Strategy

When synthesizing vocalizations, the system uses this fallback chain:

1. **Character-specific emotion preset**: `voices.json[character]["emotion_presets"][vocalization_type]`
2. **Character generic preset**: `voices.json[character]["emotion_presets"]["generic"]`
3. **Global generic preset**: `voices.json["_generic_emotions_"][vocalization_type]`
4. **No emotion**: Synthesize without emotion controls (current behavior)

## Global Generic Emotions

You can define fallback emotion presets for all characters:

```json
{
  "_generic_emotions_": {
    "grunt": {
      "emo_text": "physical grunt",
      "emo_alpha": 0.7
    },
    "yell": {
      "emo_text": "urgent yell",
      "emo_alpha": 0.6
    },
    // etc.
  }
}
```

## Example: Jaheira with Emotion Presets

```json
{
  "Jaheira": {
    "ref": "refs/jaheira_ref.wav",
    "preset": "female_mature",
    "notes": "Druid widow - Stern, Medium energy, Mature timbre",
    "status": "Locked",
    
    "emotion_presets": {
      "grunt": {
        "emo_audio_prompt": "refs/emotions/jaheira/grunt_20555.wav",
        "emo_text": "pained frustrated grunt",
        "emo_alpha": 0.85
      },
      "yell": {
        "emo_audio_prompt": "refs/emotions/jaheira/yell_20558.wav",
        "emo_text": "angry defiant yell",
        "emo_alpha": 0.75
      },
      "cry": {
        "emo_audio_prompt": "refs/emotions/jaheira/cry_42213.wav",
        "emo_text": "deep grief anguish",
        "emo_alpha": 0.9
      },
      "laugh": {
        "emo_audio_prompt": "refs/emotions/jaheira/laugh_26496.wav",
        "emo_text": "nervous awkward chuckle",
        "emo_alpha": 0.6
      },
      "cough": {
        "emo_audio_prompt": "refs/emotions/jaheira/cough_1327.wav",
        "emo_text": "sickly weak cough",
        "emo_alpha": 0.85
      }
    }
  }
}
```

## Creating Emotion References

Use the `extract_emotion_refs.py` script to build emotion reference library:

```bash
# Interactive classification
python scripts/utils/extract_emotion_refs.py --character Jaheira

# Auto-detect vocalizations
python scripts/utils/extract_emotion_refs.py --character Jaheira --auto-detect

# Show current library
python scripts/utils/extract_emotion_refs.py --character Jaheira --summary
```

This will:
1. Scan original game WAV files
2. Classify each as an emotion type (manually or auto-detect)
3. Copy clips to `refs/emotions/<character>/<emotion>_<strref>.wav`
4. Generate `refs/emotions/emotion_refs.json` mapping

## Usage in Synthesis

The enhanced `synth_batch.py` will automatically:

1. Detect vocalizations using `classify_vocalizations.py`
2. Look up emotion preset for (character, vocalization_type)
3. Pass emotion controls to Index-TTS:
   - `emo_audio_prompt`: Path to emotion reference WAV
   - `emo_text`: Emotion description text
   - `emo_alpha`: Emotion strength
4. Optionally transform text (e.g., "Gllgghh!" → "aarrgh" for better TTS)

No changes required to existing workflow - emotion synthesis is automatic when presets are configured!

## Migration Path

1. **Phase 1**: Add emotion presets for main characters (Imoen, Minsc, Jaheira)
2. **Phase 2**: Add presets for secondary companions
3. **Phase 3**: Add generic fallbacks for minor NPCs
4. **Phase 4**: Refine emo_alpha values based on quality feedback

Characters without emotion presets continue to work as before (backward compatible).
