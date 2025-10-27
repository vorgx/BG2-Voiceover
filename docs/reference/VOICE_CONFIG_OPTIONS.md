# Voice Configuration Options

Complete reference for `data/voices.json` configuration.

## Basic Configuration

```json
{
  "CharacterName": {
    "ref": "refs/character_ref.wav",
    "status": "Testing"
  }
}
```

## Available Parameters

### Core Parameters

#### `ref` (string, **required**)
Path to the voice reference audio file (WAV format).
- **Relative paths** (from project root): `"refs/jaheira_ref.wav"`
- **Absolute paths**: `"C:/path/to/reference.wav"`
- **Recommended**: 20-60 seconds of high-quality speech
- **Format**: WAV, 22050Hz, mono or stereo

#### `status` (string, optional)
Current state of the voice configuration for tracking progress.
- `"Draft"` - Initial concept, not tested
- `"Pending"` - Needs reference creation
- `"Testing"` - Currently being evaluated
- `"Locked"` - Approved and finalized
- Custom values allowed

### Advanced Parameters

#### `speed` (float, optional, default: 1.0)
Speech rate multiplier.
- **Range**: 0.5 to 2.0 (recommended: 0.8 to 1.2)
- **Examples**:
  - `0.9` - 10% slower (more deliberate)
  - `1.0` - Normal speed
  - `1.1` - 10% faster (more energetic)
- **Use cases**: Adjust pacing for character personality
- **⚠️ Note**: Triggers API mode (slower synthesis)

#### `pitch` (float, optional, default: 0.0)
Pitch shift in semitones.
- **Range**: -12 to +12 (recommended: -3 to +3)
- **Examples**:
  - `-2.0` - Lower/deeper voice
  - `0.0` - Original pitch
  - `+2.0` - Higher/brighter voice
- **Use cases**: Fine-tune voice timbre
- **⚠️ Note**: Triggers API mode (slower synthesis)

#### `preset` (string, optional)
Voice preset hint (not currently used by Index-TTS, for documentation only).
- Examples: `"female_mature"`, `"male_booming"`, `"female_gentle"`

#### `notes` (string, optional)
Human-readable description of the character and voice choices.

### Emotion Parameters (Manual Override)

Can be specified in CSV `Emotion` column or in voices.json:

#### `emo_audio_prompt` (string, optional)
Path to emotion reference clip (overrides auto-detection).
- Example: `"refs/emotions/jaheira/angry.wav"`

#### `emo_alpha` (float, optional, default: 0.7)
Emotion blending strength.
- **Range**: 0.0 to 1.0
- **Examples**:
  - `0.3` - Subtle emotional tint
  - `0.7` - Moderate emotion
  - `0.9` - Strong emotion
- **⚠️ Note**: Requires `emo_audio_prompt`

### Experimental Parameters

⚠️ **Advanced users only** - may not work as expected:

#### `interval_silence` (float, optional)
Silence duration between sentences (seconds).

#### `use_random` (bool, optional)
Enable randomization for voice variation.

#### `max_text_tokens_per_segment` (int, optional)
Maximum text length per synthesis segment.

## Complete Example

```json
{
  "Jaheira": {
    "ref": "refs/jaheira_ref.wav",
    "speed": 0.9,
    "pitch": -0.5,
    "preset": "female_mature",
    "notes": "Druid widow - Stern, deliberate pacing, slightly deeper tone",
    "status": "Locked"
  },
  "Minsc": {
    "ref": "refs/minsc_ref.wav",
    "speed": 1.1,
    "pitch": 0.0,
    "preset": "male_booming",
    "notes": "Ranger - Boisterous, high energy, faster speech",
    "status": "Testing"
  }
}
```

## Performance Notes

### CLI Mode (Fast)
Used when **no** advanced parameters are present:
- Only `ref`, `preset`, `notes`, `status`
- ~2-5 minutes per line
- Simple voice cloning from reference

### API Mode (Slower)
Triggered by **any** of these parameters:
- `speed`, `pitch`
- `emo_audio_prompt`, `emo_alpha`, `emo_text`
- `interval_silence`, `use_random`
- ~3-10 minutes per line
- Full control over synthesis

## Best Practices

### 1. Start Simple
```json
{
  "Character": {
    "ref": "refs/character_ref.wav",
    "status": "Testing"
  }
}
```
Test the base voice first before adding adjustments.

### 2. Make Small Adjustments
- Speed: ±10% (0.9 or 1.1) is usually enough
- Pitch: ±1 to ±2 semitones for subtle changes
- Avoid extreme values that make voices unnatural

### 3. Document Your Choices
```json
{
  "notes": "Speed 0.9 = more deliberate pacing for stern personality. Pitch -1 = slightly deeper for maturity."
}
```

### 4. Use Status for Tracking
- `"Draft"` → `"Pending"` → `"Testing"` → `"Locked"`
- Lock voices before full synthesis runs

### 5. Test Before Committing
Generate 10-20 test lines before synthesizing hundreds of lines.

## Common Adjustments

### Character Too Rushed
```json
{"speed": 0.9}  // Slow down 10%
```

### Voice Too High/Squeaky
```json
{"pitch": -1.5}  // Lower pitch
```

### Character Too Monotone
```json
{"emo_alpha": 0.4}  // Add subtle emotion variation
```

### Need More Energy
```json
{"speed": 1.1}  // Speed up 10%
```

## Troubleshooting

### Problem: Speed/pitch settings ignored
**Solution**: Check that synthesis shows "Generating (API)" not just "Generating"

### Problem: Voice sounds unnatural with adjustments
**Solution**: Reduce magnitude (try 0.95 instead of 0.9 for speed)

### Problem: Synthesis too slow
**Solution**: Remove `speed` and `pitch` to use faster CLI mode

### Problem: Emotion override not working
**Solution**: Ensure emotion reference file exists and path is correct
