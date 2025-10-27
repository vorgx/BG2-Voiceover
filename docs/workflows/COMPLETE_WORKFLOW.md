# Complete BG2 Voiceover Workflow

This document outlines the complete end-to-end workflow for generating voice-over content for Baldur's Gate 2, from initial data collection through final packaging.

## Overview

The workflow consists of 10 major stages that transform raw game dialogue files into fully voiced audio suitable for mod installation. The pipeline is designed to process dialogue chapter-by-chapter to maintain quality and manage scope.

---

## Stage 1: Initial Data Collection & Setup

### Purpose
Gather all required source materials and configure the system.

### Files & Directories

**Inputs:**
- `BG2 Files/Dialog Files/*.D` - WeiDU dialogue scripts extracted from the game
- `BG2 Files/dialog.tra` - Translation file containing all dialogue text with StrRef IDs
- `BG2 Files/WAV Files/` - Original game voice files (for reference/gap detection)
- `BG2 Files/Character Samples from Elevenlabs/` - High-quality voice reference clips for each speaker
- `refs/emotions/` - Emotion prompt audio files for dynamic emotion control

**Configuration:**
- `config/defaults.yaml` - System paths, Index-TTS settings, I/O directories

### Prerequisites
- Index-TTS repository cloned and configured at: `C:/Users/tenod/source/repos/TTS/index-tts/`
- Index-TTS models downloaded to: `C:/Users/tenod/source/repos/TTS/index-tts/checkpoints/`
- CUDA-enabled GPU (RTX 4090 recommended)
- Python 3.10+ with Index-TTS virtual environment set up

---

## Stage 2: Database Building

### Purpose
Create a master database of all dialogue lines with metadata.

### Script
```bash
python scripts/utils/build_complete_lines_db.py
```

### Inputs
- `BG2 Files/Dialog Files/*.D` - Parsed for dialogue structure
- `BG2 Files/dialog.tra` - Source of dialogue text
- `BG2 Files/WAV Files/` - Checked for existing voice-over references

### Outputs
**`data/all_lines.csv`** - Master dialogue database with columns:
- `StrRef` - String reference ID (unique identifier)
- `Speaker` - Character/NPC name
- `Text` - Dialogue text content
- `WAV_Reference` - Original game WAV file (if exists)
- `Chapter` - Game chapter assignment
- `Source_File` - Origin `.D` file

### What It Does
1. Scans all `.D` dialogue files
2. Extracts StrRef → Speaker mappings
3. Looks up text from `dialog.tra`
4. Cross-references existing WAV files
5. Assigns chapter metadata
6. Outputs single unified CSV

---

## Stage 3: Data Cleaning & Organization

### Purpose
Normalize text and organize data by chapter.

### Step 3A: Text Cleaning

**Script:**
```bash
python scripts/utils/clean_placeholders.py
```

**Inputs:**
- `data/all_lines.csv`

**Outputs:**
- `data/all_lines.csv` (modified in-place)

**What It Does:**
- Removes WeiDU placeholder tokens:
  - `<CHARNAME>` → "you"
  - `<PRO_HESHE>` → "they"
  - `<PRO_HIMHER>` → "them"
  - `<PRO_HISHER>` → "their"
  - `<SIRMAAM>` → "friend"
  - And ~15 other common tokens
- Normalizes punctuation and spacing
- Ensures text is TTS-friendly

### Step 3B: Chapter Splitting

**Script:**
```bash
python scripts/utils/split_chapters.py
```

**Inputs:**
- `data/all_lines.csv`

**Outputs:**
- `data/chapter1_lines.csv` - Chapter 1: Irenicus Dungeon
- `data/chapter2_lines.csv` - Chapter 2: Athkatla
- `data/chapter3_lines.csv` - Chapter 3+
- `data/chapter{n}_lines.csv` - Additional chapters
- `data/unassigned_lines.csv` - Lines without chapter metadata

**What It Does:**
Creates per-chapter subsets for targeted synthesis workflows.

---

## Stage 4: Character & Voice Configuration

### Purpose
Map speakers to voice configurations and lock final voice selections.

### Script
```bash
python scripts/utils/map_chapter1_speakers.py
```

### Inputs
- `data/chapter1_lines.csv` - List of speakers in Chapter 1
- `data/characters.csv` - Existing character metadata
- `data/voices.json` - Voice configuration database

### Outputs
- `data/characters.csv` - Updated with any missing Chapter 1 NPCs
- `data/voices.json` - Confirmed/updated voice mappings

### Manual Configuration Required

After script runs, review and lock voices in `data/voices.json`:

```json
{
  "Ilyich": {
    "ref": "BG2 Files/Character Samples from Elevenlabs/ilyich_ref.wav",
    "status": "Locked",
    "pitch_shift": -2,
    "speed": 1.1,
    "notes": "Dynamic emotion detection enabled"
  },
  "Minsc": {
    "ref": "BG2 Files/Character Samples from Elevenlabs/minsc_ref.wav",
    "status": "Locked",
    "emo_audio_prompt": "refs/emotions/heroic.wav",
    "notes": "Heroic warrior tone"
  },
  "Portal": {
    "ref": "BG2 Files/Character Samples from Elevenlabs/valygar_ref.wav",
    "status": "Locked",
    "notes": "Uses Valygar voice sample"
  }
}
```

**Key Fields:**
- `ref` - Path to reference WAV file for voice cloning
- `status` - "Locked" prevents accidental changes during synthesis
- `pitch_shift` - Semitones to shift pitch (negative = lower)
- `speed` - Playback speed multiplier (1.0 = normal)
- `emo_audio_prompt` - Path to emotion reference audio
- `emo_text` - Text-based emotion description
- `emo_alpha` - Emotion influence strength (0.0-1.0)

---

## Stage 5: Synthesis Target Generation

### Purpose
Identify which lines need voice-over generation.

### Script
```bash
python scripts/utils/filter_chapter1_for_synth.py
```

### Inputs
- `data/chapter1_lines.csv` - All Chapter 1 dialogue
- `build/OGG/*.wav` - Previously generated voice files

### Outputs
- `data/chapter1_unvoiced_only.csv` - Lines requiring synthesis

### What It Does
1. Reads all Chapter 1 lines
2. Checks if `{StrRef}.wav` exists in `build/OGG/`
3. Filters out lines that already have voice files
4. Writes remaining unvoiced lines to target CSV

**Example Output:**
```
Total Chapter 1 lines: 1,530
Already voiced: 147
Remaining to generate: 1,383
```

---

## Stage 6: Batch Synthesis (Main Pipeline)

### Purpose
Generate voice-over audio for all target lines using Index-TTS.

### Script
```bash
C:/Users/tenod/source/repos/TTS/index-tts/.venv/Scripts/python.exe scripts/core/synth_batch.py --input data/chapter1_unvoiced_only.csv
```

**⚠️ Important:** Must use Index-TTS virtual environment to access all dependencies.

### Inputs
- `data/chapter1_unvoiced_only.csv` - Lines to synthesize
- `data/voices.json` - Voice configurations
- `data/characters.csv` - Character metadata
- `config/defaults.yaml` - System configuration
- `BG2 Files/Character Samples from Elevenlabs/*.wav` - Voice reference clips
- `refs/emotions/*.wav` - Emotion prompt audio
- Index-TTS models from `C:/Users/tenod/source/repos/TTS/index-tts/checkpoints/`:
  - `gpt.pth` - GPT-based semantic model
  - `s2mel.pth` - Mel-spectrogram generator
  - `bpe.model` - Text tokenizer
  - `config.yaml` - Model configuration
  - Plus HuggingFace models (semantic_codec, campplus, bigvgan)

### Dependencies (Internal)
- `src/bg2vo/config.py` - Configuration loader
- `src/bg2vo/emotions.py` - Automatic emotion detection
- `scripts/utils/adjust_audio.py` - Audio post-processing

### Outputs
- `build/OGG/{StrRef}.wav` - Generated voice files (22050 Hz, mono WAV)

### Processing Pipeline

For each line in the input CSV:

1. **Text Sanitization**
   - Remove remaining placeholder tokens
   - Normalize punctuation and spacing
   - Clean up grammar artifacts
   - Capitalize first letter

2. **Voice Resolution**
   - Look up speaker in `voices.json`
   - Load voice reference WAV
   - Apply default fallback if speaker not found

3. **Emotion Detection** (speaker-specific)
   - For Ilyich: Auto-detect emotion from text
   - For others: Use configured emotion prompts
   - Map emotion → audio prompt path

4. **Speech Synthesis**
   - Initialize Index-TTS (once at startup, reused for all lines)
   - Pass text + voice ref + emotion config
   - Generate audio on GPU (CUDA)
   - Typical generation: ~10-11 seconds per line
   - Real-time factor (RTF): ~2.3x

5. **Audio Post-Processing**
   - Apply pitch shift (if configured)
   - Apply speed adjustment (if configured)
   - Save to `build/OGG/{StrRef}.wav`

### Performance Metrics
- GPU: CUDA device (RTX 4090)
- Speed: ~10-11 seconds per line
- RTF: 2.3 (generates 1 second of audio in 2.3 seconds)
- Model load time: ~1-2 minutes (one-time at startup)
- Estimated time for 1,383 lines: ~4 hours

### Console Output Example
```
📄 Reading lines from: data\chapter1_unvoiced_only.csv
   Total entries: 1383
🧠 Initialising Index-TTS (device=cuda:0)
>> GPT weights restored from: C:\Users\tenod\source\repos\TTS\index-tts\checkpoints\gpt.pth
>> semantic_codec weights restored from: ...
>> s2mel weights restored from: ...
>> campplus_model weights restored from: ...
>> bigvgan weights restored from: nvidia/bigvgan_v2_22khz_80band_256x
>> TextNormalizer loaded
>> bpe model loaded from: C:\Users\tenod\source\repos\TTS\index-tts\checkpoints\bpe.model
[1/1383] Ilyich -> 28533
   🎭 Emotion: angry
>> starting inference...
>> gpt_gen_time: 6.83 seconds
>> s2mel_time: 1.05 seconds
>> bigvgan_time: 0.19 seconds
>> Total inference time: 10.58 seconds
>> Generated audio length: 4.59 seconds
>> RTF: 2.3078
>> wav file saved to: C:\Users\tenod\source\repos\BG2 Voiceover\build\OGG\28533.wav
[2/1383] Minsc -> 29839
...
```

---

## Stage 7: Post-Synthesis Verification

### Purpose
Confirm all target lines have been successfully generated.

### Script
```bash
python scripts/utils/filter_chapter1_for_synth.py
```

Or for full database scan:
```bash
python scripts/utils/filter_unvoiced_lines.py
```

### Inputs
- `data/chapter1_lines.csv` (or `data/all_lines.csv`)
- `build/OGG/*.wav`

### Outputs
- Console report showing remaining gaps
- Optional: Gap report CSV

### Expected Result
After successful synthesis:
```
Total Chapter 1 lines: 1,530
Already voiced: 1,530
Remaining to generate: 0 ✓
```

If gaps remain, investigate:
- Check synthesis log for errors
- Verify problem StrRef IDs
- Re-run synthesis for failed lines

---

## Stage 8: Quality Assurance (Manual)

### Purpose
Verify audio quality and make adjustments as needed.

### Tasks

**1. Sample Listening**
- Play random WAVs from `build/OGG/`
- Check voice consistency
- Verify emotion accuracy (especially Ilyich)
- Listen for audio artifacts

**2. Spot Check Key Characters**
```bash
# Example: Check all Ilyich lines
Get-ChildItem build/OGG | Where-Object { $_.Name -match '^285\d{2}\.wav$' }
```

**3. Verify Post-Processing**
- Confirm pitch shifts applied correctly
- Check speed adjustments sound natural
- Compare to reference clips

**4. Regenerate Individual Lines (if needed)**
- Edit `data/voices.json` with new parameters
- Create single-line CSV for testing
- Re-run synthesis on specific StrRef

### Optional Manual Adjustment

If fine-tuning is needed outside the batch pipeline:

```python
import scipy.io.wavfile as wavfile
from scripts.utils.adjust_audio import change_pitch, change_speed

# Load audio
sample_rate, audio = wavfile.read('build/OGG/28533.wav')

# Apply adjustments
audio = change_pitch(audio, sample_rate, -2)  # Lower by 2 semitones
audio, sample_rate = change_speed(audio, sample_rate, 1.1)  # Speed up 10%

# Save
wavfile.write('build/OGG/28533.wav', sample_rate, audio)
```

---

## Stage 9: Packaging & Deployment

### Purpose
Prepare voice files for WeiDU mod installation.

### Files Involved
- `mod/vvoBG.tp2` - Main WeiDU installer script
- `mod/vvoBG_generated.tp2` - Auto-generated component definitions
- `mod/vvoBG/` - Final mod directory structure

### Steps

**1. Copy Generated Audio**
```powershell
# Copy Chapter 1 WAVs to mod directory
Copy-Item build/OGG/*.wav -Destination mod/vvoBG/sounds/
```

**2. Update WeiDU Scripts**
- Verify `.tp2` references correct file paths
- Update version numbers
- Add Chapter 1 component definition

**3. Run WeiDU Packaging**
```bash
weidu --make-biff mod/vvoBG.tp2
```

**4. Test Installation**
- Install mod in clean BG2 instance
- Launch game
- Trigger Chapter 1 dialogues
- Verify voice-over plays correctly

### Validation Checklist
- [ ] All Chapter 1 StrRefs have corresponding WAVs
- [ ] File sizes reasonable (~50-500 KB per file)
- [ ] Audio format: 22050 Hz, mono, 16-bit PCM WAV
- [ ] No silence-only or corrupted files
- [ ] WeiDU installation completes without errors
- [ ] In-game dialogue triggers voice playback

---

## Stage 10: Iteration for Next Chapters

### Purpose
Scale workflow to remaining game chapters.

### Process

Repeat Stages 5-9 for each subsequent chapter:

**Chapter 2: Athkatla**
```bash
# Generate targets
python scripts/utils/filter_chapter2_for_synth.py

# Synthesize
C:/Users/tenod/source/repos/TTS/index-tts/.venv/Scripts/python.exe scripts/core/synth_batch.py --input data/chapter2_unvoiced_only.csv

# Verify
python scripts/utils/filter_chapter2_for_synth.py
```

**Chapter 3+: Repeat pattern**

### Chapter-Specific Considerations

- **New Speakers:** Run `map_chapter{n}_speakers.py` to add NPCs to `characters.csv`
- **Voice Drift:** Monitor consistency across chapters, adjust references if needed
- **Performance:** Larger chapters may require overnight synthesis runs
- **QA Cadence:** More frequent spot-checks for new voice actors

### Estimated Timeline (per chapter)
- Setup & configuration: 1-2 hours
- Synthesis (1000-2000 lines): 3-6 hours
- QA & adjustments: 2-4 hours
- Packaging & testing: 1-2 hours
- **Total: 7-14 hours per chapter**

---

## Key Configuration Files

### `data/voices.json`
Central voice configuration database.

**Structure:**
```json
{
  "SpeakerName": {
    "ref": "path/to/reference.wav",
    "status": "Locked" | "In Progress" | "Testing",
    "pitch_shift": -2,
    "speed": 1.1,
    "emo_audio_prompt": "refs/emotions/emotion.wav",
    "emo_text": "confident and assertive",
    "emo_alpha": 0.8,
    "notes": "Human-readable notes"
  }
}
```

**Special Configurations:**

*Dynamic Emotion (Ilyich):*
```json
"Ilyich": {
  "ref": "BG2 Files/Character Samples from Elevenlabs/ilyich_ref.wav",
  "status": "Locked",
  "pitch_shift": -2,
  "speed": 1.1,
  "notes": "Auto-detects emotion per line"
}
```

*Shared Voice (Portal → Valygar):*
```json
"Portal": {
  "ref": "BG2 Files/Character Samples from Elevenlabs/valygar_ref.wav",
  "status": "Locked"
}
```

### `data/characters.csv`
NPC metadata and chapter tracking.

**Columns:**
- `Speaker` - Character/NPC name
- `Voice_ID` - Mapped voice reference
- `First_Appearance` - Chapter number
- `Line_Count` - Total dialogue lines
- `Notes` - Character background

### `config/defaults.yaml`
System paths and model configuration.

**Key Settings:**
```yaml
inputs:
  lines_csv: data/lines.csv
  voices_json: data/voices.json

outputs:
  ogg_dir: build/OGG

paths:
  index_tts_root: C:\\Users\\tenod\\source\\repos\\TTS\\index-tts

index_tts:
  config: checkpoints/config.yaml
  use_fp16: true
  device: cuda:0
```

### `data/all_lines.csv`
Master dialogue database - single source of truth.

**Schema:**
- `StrRef` (int) - Unique dialogue ID
- `Speaker` (string) - Character name
- `Text` (string) - Dialogue content
- `WAV_Reference` (string) - Original game WAV (if exists)
- `Chapter` (string) - Game chapter
- `Source_File` (string) - Origin `.D` file

**Sample Row:**
```csv
StrRef,Speaker,Text,WAV_Reference,Chapter,Source_File
28533,Ilyich,"You will regret your interference!",ILYIC001.WAV,Chapter 1 - Irenicus Dungeon,ILYICH.D
```

---

## Support Utilities Reference

### `scripts/utils/adjust_audio.py`

Audio post-processing functions used during synthesis.

**Functions:**

```python
def change_pitch(audio: np.ndarray, sample_rate: int, semitones: float) -> np.ndarray:
    """
    Shift audio pitch without changing speed.
    
    Args:
        audio: Input audio array (int16)
        sample_rate: Sample rate in Hz
        semitones: Semitones to shift (negative = lower, positive = higher)
    
    Returns:
        Pitch-shifted audio array
    """

def change_speed(audio: np.ndarray, sample_rate: int, factor: float) -> tuple[np.ndarray, int]:
    """
    Adjust audio playback speed without changing pitch.
    
    Args:
        audio: Input audio array (int16)
        sample_rate: Sample rate in Hz
        factor: Speed multiplier (1.0 = normal, >1.0 = faster, <1.0 = slower)
    
    Returns:
        (speed_adjusted_audio, new_sample_rate)
    """
```

**Usage in Pipeline:**
```python
# Applied automatically by synth_batch.py based on voices.json config
if pitch_shift and pitch_shift != 0:
    audio = change_pitch(audio, sample_rate, pitch_shift)

if speed and speed != 1.0:
    audio, sample_rate = change_speed(audio, sample_rate, speed)
```

### `src/bg2vo/emotions.py`

Automatic emotion detection and configuration.

**Functions:**

```python
def detect_emotion(text: str) -> str:
    """
    Analyze dialogue text and return emotion label.
    
    Currently used for Ilyich with dynamic emotion.
    
    Args:
        text: Dialogue text to analyze
    
    Returns:
        Emotion label: "angry", "confident", "threatening", "neutral", etc.
    """

def get_emotion_config(emotion: str, speaker: str) -> dict:
    """
    Map emotion label to Index-TTS emotion configuration.
    
    Args:
        emotion: Emotion label from detect_emotion()
        speaker: Character name
    
    Returns:
        dict with emo_audio_prompt, emo_alpha, etc.
    """
```

**Emotion Mapping:**
- `angry` → `refs/emotions/angry.wav`
- `confident` → `refs/emotions/confident.wav`
- `threatening` → `refs/emotions/threatening.wav`
- `neutral` → no emotion prompt

**Configuration Example:**
```python
# For Ilyich line: "You will regret your interference!"
emotion = detect_emotion(text)  # Returns "angry"
config = get_emotion_config("angry", "Ilyich")
# config = {
#     "emo_audio_prompt": "refs/emotions/angry.wav",
#     "emo_alpha": 0.8
# }
```

### `src/bg2vo/config.py`

Configuration management.

**Functions:**

```python
def load_config() -> Config:
    """
    Load configuration from config/defaults.yaml.
    
    Returns:
        Config object with validated settings
    """
```

**Config Object Structure:**
```python
config.inputs.lines_csv          # Path to lines CSV
config.inputs.voices_json        # Path to voices.json
config.outputs.ogg_dir          # Output directory for WAVs
config.paths.index_tts_root     # Index-TTS installation path
config.index_tts.config         # Model config path
config.index_tts.use_fp16       # FP16 optimization flag
config.index_tts.device         # CUDA device
```

---

## Troubleshooting

### Common Issues

**Issue: Synthesis fails with CUDA out of memory**
```
Solution: Reduce batch size or use FP16 mode
- Edit config/defaults.yaml: use_fp16: true
- Close other GPU processes
- Restart synthesis
```

**Issue: Voice doesn't match reference**
```
Solution: Check voice reference quality
- Verify reference WAV is clean (no background noise)
- Ensure 3-10 seconds of speech
- Try different reference clip from same speaker
- Check pitch_shift/speed settings in voices.json
```

**Issue: Emotion detection incorrect for Ilyich**
```
Solution: Override with manual emotion
- Add Emotion column to CSV
- Populate with desired emotion labels
- Re-run synthesis
```

**Issue: Generated audio has artifacts**
```
Solution: Check model checkpoints
- Verify Index-TTS models downloaded correctly
- Re-download bigvgan weights
- Check GPU drivers up to date
```

**Issue: Script can't find Index-TTS**
```
Solution: Verify paths in config/defaults.yaml
- index_tts_root should point to Index-TTS repo
- Use absolute paths, not relative
- Ensure .venv exists in Index-TTS directory
```

---

## Performance Optimization

### GPU Utilization
- **Goal:** Keep GPU at >90% utilization during synthesis
- **Current:** RTF ~2.3 indicates efficient GPU use
- **Bottleneck:** Model resides in GPU memory (no per-line reload)

### Batch Processing Tips
- Process 100-500 lines at a time for checkpointing
- Run overnight for large chapters (1000+ lines)
- Monitor disk space (each WAV ~50-500 KB)

### Quality vs. Speed
- `num_beams=1`, `do_sample=False` → Faster, deterministic
- Higher beams or sampling → Better quality, slower

---

## Next Steps After Chapter 1

1. **Verify Chapter 1 Complete**
   ```bash
   python scripts/utils/filter_chapter1_for_synth.py
   # Should show 0 remaining lines
   ```

2. **QA Review Chapter 1**
   - Listen to 10-20 random samples
   - Focus on key story moments
   - Get feedback from testers

3. **Package Chapter 1 Mod**
   - Create installable WeiDU package
   - Test in-game
   - Distribute beta to testers

4. **Begin Chapter 2**
   - Run `map_chapter2_speakers.py`
   - Lock new voices in `voices.json`
   - Generate `chapter2_unvoiced_only.csv`
   - Start synthesis

5. **Scale to Remaining Chapters**
   - Repeat workflow for Chapters 3-7
   - Monitor voice consistency
   - Refine emotion prompts based on feedback

---

## Appendix: File Structure

```
BG2 Voiceover/
├── BG2 Files/
│   ├── Dialog Files/          # WeiDU .D scripts
│   ├── WAV Files/             # Original game VO
│   ├── dialog.tra             # Dialogue text database
│   └── Character Samples from Elevenlabs/  # Voice references
├── build/
│   └── OGG/                   # Generated WAV output
├── config/
│   └── defaults.yaml          # System configuration
├── data/
│   ├── all_lines.csv          # Master dialogue DB
│   ├── chapter1_lines.csv     # Chapter 1 subset
│   ├── chapter1_unvoiced_only.csv  # Synthesis targets
│   ├── characters.csv         # NPC metadata
│   └── voices.json            # Voice configuration
├── docs/
│   └── workflows/
│       └── COMPLETE_WORKFLOW.md  # This document
├── mod/
│   ├── vvoBG.tp2              # WeiDU installer
│   └── vvoBG/                 # Mod package directory
├── refs/
│   └── emotions/              # Emotion prompt audio
├── scripts/
│   ├── core/
│   │   └── synth_batch.py     # Main synthesis pipeline
│   └── utils/
│       ├── build_complete_lines_db.py
│       ├── clean_placeholders.py
│       ├── split_chapters.py
│       ├── map_chapter1_speakers.py
│       ├── filter_chapter1_for_synth.py
│       ├── filter_unvoiced_lines.py
│       └── adjust_audio.py
└── src/
    └── bg2vo/
        ├── config.py          # Config loader
        └── emotions.py        # Emotion detection
```

---

## Credits & Dependencies

**Core Technologies:**
- [Index-TTS v2.0](https://github.com/index-tts/index-tts) - Zero-shot TTS with emotion control
- [WeiDU](https://weidu.org/) - Infinity Engine modding toolkit
- [ElevenLabs](https://elevenlabs.io/) - Voice reference generation
- PyTorch, CUDA - GPU acceleration
- NumPy, SciPy - Audio processing

**Team:**
- Voice direction and quality assurance
- Script development and automation
- Testing and feedback

---

## Version History

- **v1.0** (October 2025) - Initial workflow documentation
  - Chapter 1 pipeline fully operational
  - 1,383 lines synthesized successfully
  - Dynamic emotion detection for Ilyich
  - Batch synthesis optimized for GPU efficiency

---

## Contact & Support

For issues or questions about this workflow:
1. Review troubleshooting section above
2. Check `docs/` folder for additional guides
3. Consult `AGENT.md` for high-level context
4. Review archived planning docs in `archive/`
