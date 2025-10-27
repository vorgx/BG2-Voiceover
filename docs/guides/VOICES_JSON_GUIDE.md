# voices.json Configuration Guide

## Overview

`data/voices.json` maps character names to voice synthesis parameters. Supports both simple presets and advanced Index-TTS features.

## Format

### Simple Format (String)

**Legacy - still supported:**
```json
{
  "CharacterName": "preset_name_or_path"
}
```

### Advanced Format (Object)

**Recommended:**
```json
{
  "CharacterName": {
    "voice": "preset_name",           // Optional: Index-TTS preset
    "ref": "path/to/reference.wav",   // Optional: Custom reference audio
    "emo_alpha": 1.0,                  // Optional: Emotion strength (0.0-1.0)
    "emo_audio_prompt": "path.wav",    // Optional: Separate emotion reference
    "emo_text": "happy",               // Optional: Emotion text hint
    "interval_silence": 200,           // Optional: Silence between segments (ms)
    "use_random": false,               // Optional: Random variation
    "max_text_tokens_per_segment": 120 // Optional: Text chunking size
  }
}
```

---

## Parameter Reference

### Required (at least one):

#### `voice` (string)
Index-TTS preset name. Available presets:
- `narrator` - Default neutral voice
- `female_bright` - Young cheerful female
- `female_mature` - Older authoritative female  
- `female_cool` - Cold sardonic female
- `male_booming` - Deep heroic male
- `male_sardonic` - Arrogant sarcastic male
- `male_flat` - Neutral stoic male

**Example:**
```json
"Minsc": { "voice": "male_booming" }
```

#### `ref` (string, path)
Path to custom reference audio (WAV file). Use for voice cloning.

**Requirements:**
- Format: Mono, 16-bit, 22050 Hz WAV
- Duration: 20-30 seconds ideal
- Quality: Clear speech, no background noise
- See: Multi-reference creation guide

**Example:**
```json
"Imoen": { "ref": "C:\\...\\refs\\imoen_ref_multi.wav" }
```

**Can combine** `voice` + `ref`:
```json
"Viconia": {
  "voice": "female_cool",
  "ref": "refs/viconia_ref_multi.wav"
}
```

### Optional Parameters:

#### `emo_alpha` (float, 0.0-1.0)
Emotion strength multiplier.
- `0.0` = Monotone, no emotion
- `1.0` = Full emotion (default)
- `0.5` = Subdued emotion

**Use case:** Tone down overly dramatic synthesis

**Example:**
```json
"Keldorn": {
  "ref": "refs/keldorn_ref.wav",
  "emo_alpha": 0.7  // Calmer, more stoic
}
```

#### `emo_audio_prompt` (string, path)
Separate audio file for emotion reference (distinct from voice reference).

**Use case:** Clone voice from one file, emotion from another

**Example:**
```json
"Aerie": {
  "ref": "refs/aerie_voice.wav",          // Voice characteristics
  "emo_audio_prompt": "refs/aerie_shy.wav" // Timid emotion
}
```

#### `emo_text` (string)
Text hint for desired emotion. Guides the emotion model.

**Common values:**
- `"happy"`, `"sad"`, `"angry"`, `"fearful"`
- `"neutral"`, `"excited"`, `"calm"`

**Use case:** Override auto-detected emotion

**Example:**
```json
"Minsc": {
  "voice": "male_booming",
  "emo_text": "excited"  // Always enthusiastic
}
```

**Note:** Requires setting `use_emo_text: true` (automatic when `emo_text` present)

#### `interval_silence` (int, milliseconds)
Silence duration between synthesized segments.

**Default:** 200ms
**Range:** 0-1000ms

**Use case:** Adjust pacing for long sentences

**Example:**
```json
"Edwin": {
  "voice": "male_sardonic",
  "interval_silence": 300  // Slower, more dramatic pauses
}
```

#### `use_random` (boolean)
Enable random variation in synthesis.

**Default:** `false`
**Effect:** Slight variations in prosody/timing

**Use case:** Make repeated lines sound less identical

**Example:**
```json
"Narrator": {
  "voice": "narrator",
  "use_random": true  // Variety for common phrases
}
```

#### `max_text_tokens_per_segment` (int)
Maximum tokens per synthesis segment (for long text).

**Default:** 120
**Range:** 50-200

**Use case:** Adjust chunking for very long dialogue

**Example:**
```json
"Elminster": {
  "voice": "male_mature",
  "max_text_tokens_per_segment": 150  // Longer segments for speeches
}
```

---

## Complete Examples

### Example 1: Simple Preset
```json
{
  "Minsc": {
    "voice": "male_booming"
  }
}
```

### Example 2: Multi-Reference Clone
```json
{
  "Imoen": {
    "ref": "C:\\Users\\tenod\\source\\repos\\BG2 Voiceover\\refs\\imoen_ref_multi.wav",
    "emo_alpha": 1.0,
    "interval_silence": 200
  }
}
```

### Example 3: Preset + Tuning
```json
{
  "Viconia": {
    "voice": "female_cool",
    "emo_alpha": 0.8,
    "interval_silence": 250
  }
}
```

### Example 4: Advanced Clone + Emotion
```json
{
  "Aerie": {
    "ref": "refs/aerie_ref_multi.wav",
    "emo_text": "fearful",
    "emo_alpha": 0.9,
    "interval_silence": 150
  }
}
```

### Example 5: Fallback with Default
```json
{
  "_default_": {
    "voice": "narrator"
  },
  "Imoen": {
    "ref": "refs/imoen_ref_multi.wav"
  },
  "Minsc": {
    "voice": "male_booming"
  },
  "UnknownNPC": {
    // Will use _default_ if not found
  }
}
```

---

## Migration from Old Format

### Before (v1):
```json
{
  "_default_": "narrator",
  "Imoen": "refs/imoen_ref.wav",
  "Minsc": "male_booming"
}
```

### After (v2):
```json
{
  "_default_": {
    "voice": "narrator"
  },
  "Imoen": {
    "ref": "refs/imoen_ref_multi.wav",
    "emo_alpha": 1.0
  },
  "Minsc": {
    "voice": "male_booming"
  }
}
```

**Backward Compatible:** Old string format still works!

---

## Performance Notes

### CLI vs API

**Simple config** (just `voice` or `ref`):
- Uses **CLI mode** (fast, external process)
- Best for batch processing

**Advanced config** (with `emo_alpha`, `interval_silence`, etc.):
- Uses **Python API** (slower startup, model loads in-process)
- Best for quality tuning

### Recommendations:

1. **Start with CLI** (simple presets or refs)
2. **Add advanced params** only when needed for quality
3. **Batch same-config** characters together for efficiency

---

## Troubleshooting

### "No voice found for character"
- Check spelling of character name in lines.csv
- Add `"_default_"` fallback

### "Reference file not found"
- Use **absolute paths** (Windows: `C:\\...`)
- Or relative to project root: `refs/...`

### "Synthesis sounds wrong"
- Try adjusting `emo_alpha` (0.6-1.0 range)
- Check reference audio quality (clear, 20-30s, multi-sample)
- Verify text sanitization (no tags)

### "Very slow synthesis"
- Advanced params trigger API mode (slower)
- Use simple presets for initial testing
- Consider GPU (`cuda`) vs CPU

---

## Best Practices

### For Multi-Reference Clones:
```json
{
  "ref": "refs/character_ref_multi.wav",  // 20-30s, 5-10 samples
  "emo_alpha": 1.0,                        // Full emotion
  "interval_silence": 200                  // Standard pacing
}
```

### For Preset-Based:
```json
{
  "voice": "appropriate_preset",
  "emo_alpha": 0.8,           // Slightly subdued
  "interval_silence": 200
}
```

### For Hybrid (Best of Both):
```json
{
  "voice": "female_mature",           // Baseline characteristics
  "ref": "refs/jaheira_ref.wav",      // Fine-tune with reference
  "emo_alpha": 0.9,                   // Mature, controlled emotion
  "interval_silence": 250             // Measured pacing
}
```

---

**Version:** 2.0 (Advanced Parameters)  
**Updated:** October 26, 2025  
**Status:** Production-ready with backward compatibility
