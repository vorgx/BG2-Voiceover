# Chapter 1 Full Synthesis - Handover Document

## Current Status (October 27, 2025)

### ✅ Completed Phases

#### Phase 1-3: Main Companions (LOCKED)
- **Jaheira**: 31.4s reference, 516 lines, female_mature preset
- **Minsc**: 64.6s reference, 257 lines, male_booming preset  
- **Imoen**: 59.2s reference, 63 lines, female_bright preset
- All tested and approved by user

#### Phase 4: Secondary Characters (LOCKED)
- **Yoshimo**: 50.6s reference, 37 lines, male_smooth preset
- **Valygar**: 44.0s reference, 8 lines, male_flat preset
- **Rielev**: 17.7s reference, 16 lines, male_deep preset
- **Dryad**: 8.1s reference, 2 lines, female_gentle preset

#### Phase 4: Ilyich (Custom ElevenLabs Voice - READY)
- **Reference**: 30.9s ElevenLabs custom voice (v3)
- **Lines**: 4 lines
- **Special Processing**:
  - Emotion vectors: 30% Angry, 15% Disgusted (auto-detected)
  - Pitch shift: -2 semitones (post-processing)
  - Speed: 0.95x (5% slower, post-processing)
  - Interval silence: 0.45 seconds (longer pauses)
- **Status**: Ready for testing, all parameters tuned

### 📊 Chapter 1 Statistics
- **Total Lines**: 905
- **Total Speakers**: 8
- **Voice References**: All created and locked
- **Estimated Generation Time**: 1-2 hours with CUDA GPU

---

## Next Step: Full Chapter 1 Synthesis

### Prerequisites Check
1. ✅ All 8 voice references exist in `refs/` directory
2. ✅ `data/chapter1_split.csv` exists with all 905 lines
3. ✅ `voices.json` configured for all speakers
4. ✅ CUDA GPU acceleration enabled in `synth.py`
5. ✅ Emotion system active ONLY for Ilyich
6. ✅ Post-processing configured for Ilyich (pitch, speed, pauses)

### Command to Execute

```powershell
# Navigate to project root
cd "C:\Users\tenod\source\repos\BG2 Voiceover"

# Run full Chapter 1 synthesis
C:\Users\tenod\source\repos\TTS\index-tts\.venv\Scripts\python.exe scripts\core\synth.py --input data\chapter1_split.csv
```

### What Will Happen
1. **System reads** `data/chapter1_split.csv` (905 lines, 8 speakers)
2. **For each line**:
   - Loads speaker config from `voices.json`
   - Loads voice reference from `refs/` directory
   - **Ilyich only**: Auto-detects emotion → uses emotion vectors
   - Generates audio via Index-TTS (CUDA GPU accelerated)
   - **Ilyich only**: Applies post-processing (pitch -2, speed 0.95, pauses 0.45s)
   - Saves to `build/OGG/{StrRef}.wav`
3. **Skips existing files** (resume capability if interrupted)

### Expected Output
- **Location**: `C:\Users\tenod\source\repos\BG2 Voiceover\build\OGG\`
- **Files**: 905 WAV files named by StrRef (e.g., `18384.wav`)
- **Duration**: Varies by line length
- **Quality**: 22kHz, mono, 16-bit PCM WAV

### Monitoring Progress
The terminal will show:
```
📄 Reading lines from: data\chapter1_split.csv
  🎭 Auto-detected emotion for Ilyich: angry  # Only for Ilyich lines
  🎭 Using emotion: angry
  Generating (API): {StrRef} -> build\OGG\{StrRef}.wav
  🎵 Applying post-processing (pitch_shift=-2, speed=0.95)  # Only for Ilyich
```

### Estimated Timeline
- **With CUDA GPU**: ~1-2 hours
- **Without GPU**: ~8-15 hours
- **Lines per minute**: ~7-10 (varies by length and processing)

### Interruption & Resume
- If interrupted (Ctrl+C), simply re-run the same command
- System automatically skips files that already exist in `build/OGG/`
- Deletes incomplete files on error, so safe to restart

---

## Configuration Files Reference

### 1. `data/voices.json` - Speaker Configurations

**Standard Speakers** (No post-processing):
```json
{
  "Jaheira": {
    "ref": "refs/jaheira_ref.wav",
    "preset": "female_mature",
    "status": "Locked"
  },
  "Minsc": {
    "ref": "refs/minsc_ref.wav",
    "preset": "male_booming",
    "status": "Locked"
  },
  // ... similar for Imoen, Yoshimo, Valygar, Rielev, Dryad
}
```

**Ilyich** (Special processing):
```json
{
  "Ilyich": {
    "ref": "refs/ilyich_ref.wav",
    "preset": "male_gruff",
    "pitch_shift": -2,
    "speed": 0.95,
    "interval_silence": 0.45,
    "notes": "ElevenLabs custom voice v3, deeper pitch, 5% slower, longer pauses",
    "status": "Ready for testing"
  }
}
```

### 2. `src/bg2vo/emotions.py` - Emotion Vectors

**Current Settings** (All emotions capped at 30% max):
```python
emotion_vectors = {
    "angry": {
        "vector": [0.0, 0.3, 0.0, 0.0, 0.15, 0.0, 0.0, 0.0],  # 30% Angry, 15% Disgusted
    },
    # Format: [Happy, Angry, Sad, Afraid, Disgusted, Melancholic, Surprised, Calm]
}
```

**Emotion Detection Logic**:
- Angry keywords: "kill", "die", "death", "fight", "attack", "no mercy", etc.
- Multiple `!` indicates anger
- Only applied to Ilyich (other speakers bypass emotion system)

### 3. `scripts/core/synth.py` - Main Synthesis Logic

**Key Features**:
- CUDA GPU acceleration: `-d cuda` flag (line 186)
- Emotion detection: Only for `speaker.lower() == "ilyich"` (lines 154-165)
- Post-processing: Applies pitch/speed/pauses after generation (lines 289-306)
- API mode: Triggered for emotion vectors or advanced parameters
- CLI mode: Fallback for simple cases

---

## System Architecture

### Python Environments
1. **Main Environment** (Python 3.13.9)
   - Location: `C:\Users\tenod\AppData\Local\Programs\Python\Python313`
   - Packages: librosa 0.11.0, scipy 1.16.2, numpy, pandas
   - Purpose: Reference building, audio post-processing, utilities

2. **Index-TTS Environment** (Python 3.10.19)
   - Location: `C:\Users\tenod\source\repos\TTS\index-tts\.venv`
   - Purpose: TTS generation (isolated from main environment)
   - Executable: `indextts.exe` for CLI, `python.exe` for API

### Key Directories
```
BG2 Voiceover/
├── data/
│   ├── chapter1_split.csv          # 905 lines to synthesize
│   ├── voices.json                 # Speaker configurations
│   └── temp_ilyich.csv             # Test file (4 lines)
├── refs/
│   ├── jaheira_ref.wav             # Voice references
│   ├── minsc_ref.wav
│   ├── imoen_ref.wav
│   ├── yoshimo_ref.wav
│   ├── valygar_ref.wav
│   ├── rielev_ref.wav
│   ├── dryad_ref.wav
│   └── ilyich_ref.wav              # ElevenLabs v3
├── build/OGG/                      # Output directory (905 WAV files)
├── scripts/
│   ├── core/
│   │   └── synth.py                # Main synthesis orchestrator
│   └── utils/
│       ├── adjust_audio.py         # Post-processing (pitch/speed)
│       └── build_ilyich_ref.py     # ElevenLabs MP3 → WAV converter
├── src/bg2vo/
│   ├── emotions.py                 # Emotion detection & vectors
│   ├── voices.py                   # Voice configuration loader
│   └── config.py                   # System configuration
└── BG2 Files/
    └── Character Samples from Elevenlabs/
        └── ilyic v3.mp3            # Source for Ilyich reference
```

### Index-TTS Integration
- **Location**: `C:\Users\tenod\source\repos\TTS\index-tts`
- **Config**: `checkpoints/config.yaml`
- **Models**: `checkpoints/gpt.pth`, `s2mel.pth`, etc.
- **Modes**:
  - **CLI**: Simple, fast, no advanced features
  - **API**: Required for emotion vectors, interval_silence, speed

---

## Workflows Documented

### 1. Standard Speaker Workflow
```
1. Extract audio clips from BG2 original files
2. Run build script (e.g., build_jaheira_ref.py)
3. Concatenate clips → single WAV reference
4. Update voices.json with speaker config
5. Test with 10 sample lines
6. User approval → Lock voice
```

### 2. Custom ElevenLabs Voice Workflow (Ilyich)
```
1. Analyze character with character_profile.py
2. Generate prompt from analysis output
3. Create voice on ElevenLabs website
4. Download MP3 (ilyic v3.mp3)
5. Run build_ilyich_ref.py (converts MP3 → WAV)
6. Update voices.json with processing parameters
7. Configure emotion detection in emotions.py
8. Test with sample lines
9. Iterate on pitch/speed/pauses/emotion strength
10. User approval → Lock voice
```

### 3. Emotion Vector Workflow
```
1. Define emotion vectors in emotions.py (8D array)
2. Set emotion cap (currently 30% max for subtlety)
3. Enable emotion detection for specific speaker in synth.py
4. System auto-detects emotion from text
5. Applies emotion vector during API generation
6. No post-processing needed (built into synthesis)
```

### 4. Post-Processing Workflow (Pitch/Speed/Pauses)
```
1. Set parameters in voices.json:
   - pitch_shift: semitones (-2 = slightly deeper)
   - speed: multiplier (0.95 = 5% slower)
   - interval_silence: seconds (0.45 = longer pauses)
2. synth.py triggers API mode (for interval_silence)
3. Index-TTS generates base audio
4. Post-processing applies pitch/speed via scipy
5. Final WAV saved to build/OGG/
```

---

## Troubleshooting Guide

### Issue: Synthesis is slow
**Check**: Is CUDA enabled?
```powershell
nvidia-smi  # Should show GPU usage when generating
```
**Fix**: Line 186 in `synth.py` should have `"-d", "cuda"`

### Issue: Emotion not applying
**Check**: Is speaker "Ilyich"?
- Emotion detection only active for Ilyich (lines 154-165 in `synth.py`)
**Check**: Is API mode triggered?
- Look for "Generating (API)" in terminal output
- If seeing "Generating:" without "(API)", emotion won't apply

### Issue: Pitch shift error
**Problem**: Function signature mismatch
**Fix**: Ensure `change_pitch(audio, sr, pitch_shift)` order is correct (lines 296-306)

### Issue: Files not generating
**Check 1**: Do files already exist? System skips existing files
**Check 2**: Is voices.json valid? Speaker must exist in config
**Check 3**: Is reference file present? Check `refs/{speaker}_ref.wav`

### Issue: Audio quality poor
**Check 1**: Is reference long enough? (Minimum ~8-10 seconds)
**Check 2**: Is reference clean? (No background noise, consistent quality)
**Check 3**: Are parameters too extreme? (pitch_shift > ±6 degrades quality)

---

## Next Steps After Synthesis

### Phase 7: Deploy & Test

1. **Convert WAV to OGG**:
   ```powershell
   # Use ffmpeg or similar to convert build/OGG/*.wav to .ogg format
   # BG2 mod requires Ogg Vorbis format
   ```

2. **Deploy to Mod Structure**:
   ```
   BG2 Voiceover Mod/
   ├── audio/
   │   └── [language]/
   │       └── *.ogg files (named by StrRef)
   ├── setup.tp2              # WeiDU installer script
   └── README.md
   ```

3. **Install with WeiDU**:
   ```cmd
   setup-bg2voiceover.exe --install
   ```

4. **In-Game Testing**:
   - Start new BG2EE game
   - Play through Chapter 1
   - Verify all dialogue plays correctly
   - Check for:
     - Voice matches character personality
     - Audio quality is consistent
     - No glitches or cutoffs
     - Timing syncs with text

---

## Important Notes

### Emotion System
- **Currently enabled**: Ilyich only
- **Cap**: 30% maximum intensity for all emotions
- **Rationale**: Higher values caused unwanted artifacts (laughter, over-acting)
- **To extend**: Modify line 156-160 in `synth.py` to add more speakers

### Post-Processing Limits
- **Pitch shift**: Keep within ±6 semitones (beyond causes distortion)
- **Speed**: Range 0.5-1.5x (too slow/fast sounds unnatural)
- **Interval silence**: Range 0.1-1.0 seconds (0.45s is balanced)

### Performance
- **GPU recommended**: 5-10x faster than CPU
- **RAM usage**: ~8GB during generation
- **Disk space**: ~2-3GB for 905 WAV files

### Voice Reference Quality
- **Minimum length**: 8-10 seconds
- **Optimal length**: 20-60 seconds
- **Content**: Varied speech (different emotions, sentence structures)
- **Quality**: Clean, no background noise, consistent volume

---

## Quick Start Command

Once you're ready in the new chat, simply run:

```powershell
cd "C:\Users\tenod\source\repos\BG2 Voiceover"
C:\Users\tenod\source\repos\TTS\index-tts\.venv\Scripts\python.exe scripts\core\synth.py --input data\chapter1_split.csv
```

Monitor progress in terminal. Expected completion: 1-2 hours with GPU.

---

## Contact Context

**Project**: Baldur's Gate 2 Enhanced Edition - Voice Over Mod
**Chapter**: Chapter 1 (Irenicus Dungeon)
**Goal**: Full voice acting for all dialogue
**Approach**: Index-TTS v2.0 with custom voice references
**Special Features**: Emotion vectors, post-processing, ElevenLabs integration

---

*Document created: October 27, 2025*
*Status: Ready for Chapter 1 Full Synthesis*
