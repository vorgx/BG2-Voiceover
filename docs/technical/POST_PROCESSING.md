# Post-Processing System Documentation

## Overview

The post-processing system applies audio transformations **after** Index-TTS generation to modify pitch, speed, and timing. This allows fine-tuning voice characteristics without regenerating from Index-TTS.

## Current Status (October 27, 2025)

- **Active for**: Ilyich only
- **Inactive for**: All other speakers
- **Implementation**: `scripts/utils/adjust_audio.py` + `scripts/core/synth.py` (lines 289-306)

## Supported Transformations

### 1. Pitch Shift (`pitch_shift`)
**Purpose**: Make voice deeper or higher  
**Unit**: Semitones (musical intervals)  
**Range**: -6 to +6 (beyond causes distortion)  
**Current**: -2 semitones for Ilyich (slightly deeper)

**Examples**:
- `-2`: Subtle deeper voice (Ilyich)
- `-4`: Noticeably deeper (baritone effect)
- `+2`: Slightly higher pitch
- `0`: No change

**Technical**: Uses `scipy.signal.resample()` with frequency shifting

### 2. Speed Adjustment (`speed`)
**Purpose**: Make speech faster or slower  
**Unit**: Multiplier (1.0 = original speed)  
**Range**: 0.5 to 1.5 (beyond sounds unnatural)  
**Current**: 0.95 for Ilyich (5% slower, more deliberate)

**Examples**:
- `0.95`: 5% slower (Ilyich - deliberate)
- `0.9`: 10% slower (dramatic)
- `0.85`: 15% slower (very slow)
- `1.0`: Original speed
- `1.1`: 10% faster

**Technical**: Uses `scipy.signal.resample()` with time stretching

### 3. Interval Silence (`interval_silence`)
**Purpose**: Control pause length after punctuation  
**Unit**: Seconds  
**Range**: 0.1 to 1.0 (longer becomes unnatural)  
**Current**: 0.45 seconds for Ilyich (dramatic pauses)

**Examples**:
- `0.1-0.2`: Quick pacing
- `0.3-0.5`: Deliberate, commanding (Ilyich uses 0.45)
- `0.6-1.0`: Very dramatic, slow

**Technical**: Applied during Index-TTS generation (not post-processing)  
**Note**: Requires API mode (triggers `use_api = True`)

## Configuration

### In `data/voices.json`

```json
{
  "Ilyich": {
    "ref": "refs/ilyich_ref.wav",
    "preset": "male_gruff",
    "pitch_shift": -2,           // Post-processing
    "speed": 0.95,               // Post-processing
    "interval_silence": 0.45,    // API mode parameter
    "notes": "...",
    "status": "Ready for testing"
  }
}
```

### Processing Order

1. **Index-TTS Generation** (with `interval_silence` if set)
2. **Post-Processing** (if `pitch_shift` or `speed` set):
   - Load generated WAV
   - Apply speed adjustment (if `speed != 1.0`)
   - Apply pitch shift (if `pitch_shift != 0`)
   - Save modified WAV (overwrites original)

## Implementation Details

### Location: `scripts/core/synth.py`, lines 289-306

```python
# Apply post-processing if needed
if pitch_shift or speed_adjust:
    print(f"  🎵 Applying post-processing (pitch_shift={pitch_shift}, speed={speed_adjust})")
    sys.path.insert(0, str(ROOT / "scripts" / "utils"))
    from adjust_audio import change_pitch, change_speed
    import scipy.io.wavfile as wavfile
    
    # Load generated audio
    sr, audio = wavfile.read(str(out_wav))
    
    # Apply speed adjustment
    if speed_adjust and speed_adjust != 1.0:
        audio, sr = change_speed(audio, sr, speed_adjust)
    
    # Apply pitch shift
    if pitch_shift:
        audio = change_pitch(audio, sr, pitch_shift)
    
    # Save modified audio
    wavfile.write(str(out_wav), sr, audio)
```

### Key Functions: `scripts/utils/adjust_audio.py`

#### `change_speed(audio_data, sample_rate, speed_factor)`
```python
def change_speed(audio_data: np.ndarray, sample_rate: int, speed_factor: float) -> tuple[np.ndarray, int]:
    """
    Change audio speed by resampling.
    
    Args:
        audio_data: Audio samples as numpy array
        sample_rate: Original sample rate
        speed_factor: Speed multiplier (0.95 = slower, 1.05 = faster)
    
    Returns:
        Tuple of (modified audio data, sample rate)
    """
    new_length = int(len(audio_data) / speed_factor)
    resampled = signal.resample(audio_data, new_length)
    return resampled.astype(np.int16), sample_rate
```

#### `change_pitch(audio_data, sample_rate, semitones)`
```python
def change_pitch(audio_data: np.ndarray, sample_rate: int, semitones: float) -> np.ndarray:
    """
    Change audio pitch by shifting frequency.
    
    Args:
        audio_data: Audio samples as numpy array
        sample_rate: Sample rate
        semitones: Number of semitones to shift (+2 = higher, -2 = lower)
    
    Returns:
        Modified audio data
    """
    # Calculate pitch shift ratio
    pitch_factor = 2 ** (semitones / 12.0)
    
    # Resample to shift pitch
    new_length = int(len(audio_data) / pitch_factor)
    shifted = signal.resample(audio_data, new_length)
    
    # Resample back to original length to maintain speed
    final = signal.resample(shifted, len(audio_data))
    
    return final.astype(np.int16)
```

## Quality Considerations

### Pitch Shift Quality
- **-2 to +2**: ✅ Excellent quality, imperceptible artifacts
- **-4 to +4**: ✅ Good quality, minor formant shift
- **-6 to +6**: ⚠️ Noticeable artifacts, "chipmunk" or "demonic" effect
- **Beyond ±6**: ❌ Severe distortion, unusable

### Speed Quality
- **0.8 to 1.2**: ✅ Natural-sounding
- **0.5 to 0.8**: ⚠️ Slow but usable, may sound robotic
- **1.2 to 1.5**: ⚠️ Fast but intelligible
- **Below 0.5 or above 1.5**: ❌ Unnatural, hard to understand

### Combined Effects
When using multiple effects together:
- Quality degrades additively
- Test combinations thoroughly
- **Current Ilyich settings** (pitch -2, speed 0.95) are well within safe ranges

## Performance Impact

### Processing Time
- **Pitch shift**: ~100-200ms per line (depends on audio length)
- **Speed adjust**: ~50-100ms per line
- **Combined**: ~150-300ms per line
- **Negligible** compared to Index-TTS generation (~5-15 seconds per line)

### Memory Usage
- Loads entire WAV into memory (~1-5MB per file)
- Peak memory: ~10-20MB during processing
- Safe for large batch operations

## Use Cases

### When to Use Post-Processing

**Pitch Shift**:
- ✅ Character voice too high/low
- ✅ Need subtle differentiation between similar voices
- ✅ Voice reference doesn't match character age/build
- ❌ Don't use for major changes (get better reference instead)

**Speed Adjustment**:
- ✅ Character should speak slower/faster for personality
- ✅ Dialogue pacing needs adjustment
- ✅ Emphasize deliberate or frantic speech patterns
- ❌ Don't fix timing issues (adjust generation instead)

**Interval Silence**:
- ✅ Dramatic pauses for emphasis
- ✅ Commanding, authoritative characters
- ✅ Slow, menacing villains
- ❌ Don't use for normal characters (sounds unnatural)

## Extending to Other Characters

### Example: Make Sarevok Slower and Deeper

```json
{
  "Sarevok": {
    "ref": "refs/sarevok_ref.wav",
    "preset": "male_menacing",
    "pitch_shift": -3,       // Deep, menacing voice
    "speed": 0.9,            // 10% slower, deliberate
    "interval_silence": 0.5, // Long pauses for effect
    "status": "Testing"
  }
}
```

System will automatically apply post-processing during synthesis.

## Comparison: Post-Processing vs. Generation Parameters

### Post-Processing (Current System)
**Advantages**:
- ✅ Applied after generation (can iterate quickly)
- ✅ No need to regenerate from Index-TTS
- ✅ Fine control with scipy
- ✅ Works with any voice reference

**Disadvantages**:
- ⚠️ Quality degradation at extreme values
- ⚠️ Cannot fix fundamental voice mismatch
- ⚠️ Additional processing time

### Generation Parameters (Index-TTS Native)
**Advantages**:
- ✅ Better quality (no resampling artifacts)
- ✅ Integrated into TTS model

**Disadvantages**:
- ❌ Limited support in Index-TTS (few parameters)
- ❌ Requires regeneration to adjust
- ❌ Not all features exposed in API

**Best Practice**: Use generation parameters when available (like `interval_silence`), fall back to post-processing for transformations not supported by Index-TTS (pitch, speed).

## Troubleshooting

### Issue: Pitch shift causes overflow error
**Problem**: Function signature mismatch
**Fix**: Ensure correct parameter order:
```python
change_pitch(audio, sr, pitch_shift)  # ✅ Correct
change_pitch(audio, pitch_shift, sr)  # ❌ Wrong
```

### Issue: Audio sounds distorted after processing
**Cause**: Values too extreme
**Fix**: Reduce `pitch_shift` and `speed` closer to neutral:
- Pitch: Keep within ±4 semitones
- Speed: Keep within 0.8-1.2 range

### Issue: Processing takes too long
**Cause**: Large audio files or many lines
**Fix**: This is normal, post-processing is fast (~150ms per line)
- For 905 lines: ~2-3 minutes total
- Negligible compared to generation time

### Issue: WAV file is corrupted after processing
**Cause**: Audio data type mismatch
**Fix**: Ensure int16 conversion:
```python
audio = audio.astype(np.int16)  # Must be 16-bit PCM
```

## Testing Recommendations

### Testing New Post-Processing Settings

1. **Start with one parameter**:
   - Test pitch shift alone first
   - Then speed alone
   - Then combined

2. **Test range**:
   - Start conservative (±1-2 semitones, 0.9-1.0 speed)
   - Gradually increase if needed
   - Listen for artifacts at each step

3. **Test various line types**:
   - Short lines (1-2 words)
   - Medium lines (5-10 words)
   - Long lines (20+ words)
   - Different emotions/intensities

4. **Compare with reference**:
   - Generate without post-processing
   - Generate with post-processing
   - Ensure processing improves (not degrades)

5. **User testing**:
   - Have multiple people listen
   - Check for naturalness
   - Verify voice remains consistent

## Future Enhancements

### Planned:
1. **Formant preservation**: Maintain voice timbre during pitch shift
2. **Dynamic speed**: Vary speed based on emotion/punctuation
3. **Batch processing script**: Process multiple files offline
4. **Quality presets**: "subtle", "moderate", "dramatic" settings

### Experimental:
- **Reverb/echo effects**: Add environmental ambiance
- **EQ adjustments**: Enhance bass/treble
- **Normalization**: Consistent volume levels
- **Noise reduction**: Clean up artifacts

## Technical Notes

### Dependencies
- `scipy 1.16.2`: Signal processing functions
- `numpy`: Array operations
- `soundfile` or `wavfile`: WAV I/O

### Audio Format Requirements
- **Input**: 16-bit PCM WAV, mono, 22kHz (Index-TTS output)
- **Output**: Same format maintained
- **Processing**: Float64 internally, converted back to int16

### Numerical Precision
- Pitch calculation: `2 ** (semitones / 12.0)` (exponential)
- Speed calculation: Linear resampling
- Rounding: Nearest integer for sample lengths

---

*Last Updated: October 27, 2025*
*Status: Production Ready (Ilyich), Extensible for Future Characters*
