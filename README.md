# BG2 Voiceover Automation

## Overview

This project uses **Index-TTS** to generate voice lines for Baldur's Gate II Enhanced Edition. The workflow synthesizes speech from game dialogue text, packages it with WeiDU, and installs it into BG2EE so lines play in-game.

---

## Prerequisites

### 1. Index-TTS Installation
- Clone and set up Index-TTS from: https://github.com/MLo7Ghinsan/iNDEX-tts
- Location: `C:\Users\tenod\source\repos\TTS\index-tts`
- Install into a Python virtual environment at `C:\Users\tenod\source\repos\TTS\index-tts\.venv`
- Download checkpoints into `C:\Users\tenod\source\repos\TTS\index-tts\checkpoints`
- Ensure `checkpoints/config.yaml` is properly configured

### 2. WeiDU
- WeiDU installer stub: `mod/setup-vvoBG.exe` (v24900 or later)
- Used to package and install audio overrides into BG2EE

### 3. BG2EE Installation
- Baldur's Gate II Enhanced Edition must be installed
- Example path: `E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition`

### 4. Reference Audio
- Place reference voice files in `refs/` (e.g., `refs/imoen_ref.wav`)
- Used by Index-TTS to clone speaker characteristics

---

## Project Structure

```
BG2 Voiceover/
├── data/                  # Active datasets
│   ├── lines.csv          # Master dialogue dataset
│   ├── voices.json        # Voice configuration (production)
│   ├── characters.csv     # Character metadata library
│   ├── chapter1_lines.csv # Chapter 1 dialogue
│   └── chapter1_split/    # Split files for parallel processing
├── config/                # Configuration templates
│   ├── defaults.yaml      # Default paths and settings
│   └── voices.sample.json # Voice preset staging/template
├── refs/                  # Voice reference audio
│   └── imoen_ref.wav      # Reference audio for voice cloning
├── scripts/               # Python automation tools
│   └── synth.py           # Main synthesis script
├── src/bg2vo/             # Core Python package
│   ├── config.py          # Configuration loader
│   ├── lines.py           # CSV processing
│   ├── voices.py          # Voice preset handling
│   └── audit.py           # Dialogue auditing
├── tests/                 # Test suite
├── build/                 # Build outputs
│   └── OGG/               # Generated WAV files (e.g., 38606.wav)
├── mod/                   # WeiDU mod structure
│   ├── setup-vvoBG.exe    # WeiDU installer stub
│   ├── vvoBG.tp2          # WeiDU mod definition
│   └── vvoBG/OGG/         # Audio staged for WeiDU (e.g., OH38606.wav)
├── docs/                  # Documentation
│   ├── getting-started/   # Quickstart and workflow guides
│   ├── guides/            # How-to guides
│   ├── reference/         # Technical reference
│   └── dev/               # Development docs
├── archive/               # Historical documents
└── BG2 Files/             # Game data exports
    ├── dialog.tra         # Extracted BG2 dialogue strings
│   └── WAV Files/         # Original BG2 audio files
└── README.md              # This file
```

---

## Documentation

- **[Complete Workflow](docs/workflows/COMPLETE_WORKFLOW.md)** - **START HERE**: Comprehensive end-to-end workflow covering all 10 stages from data collection through packaging
- **[AGENT.md](AGENT.md)** - AI agent guide (file placement, workflows, patterns)
- **[Getting Started](docs/getting-started/)** - Quick start guide and workflow
- **[Integration Status](docs/getting-started/INTEGRATION_STATUS.md)** - Current testing status
- **[Chapter Pipeline](docs/getting-started/CHAPTER_PIPELINE.md)** - Complete chapter workflow
- **[Guides](docs/guides/)** - How-to guides for specific tasks
- **[Reference](docs/reference/)** - Technical architecture and API docs
- **[Development](docs/dev/)** - Contributing and development guidelines

---

## Step 1: Configure Dialogue Lines

### `data/lines.csv`

Define which lines to synthesize:

```csv
StrRef,Speaker,Text
38606,Imoen,"Wow, a golem. Powerful magic stuff. Odd that it's not hostile. I suppose its maker didn't expect us to escape, so it never got orders for restraining us."
```

- **StrRef**: Game string reference number (from `dialog.tlk`)
- **Speaker**: Character name (must match a key in `voices.json`)
- **Text**: Dialogue text to synthesize

### `data/voices.json`

Map speakers to voices:

```json
{
  "_default_": "narrator",
  "Imoen": "C:\\Users\\tenod\\source\\repos\\BG2 Voiceover\\refs\\imoen_ref.wav",
  "Minsc": "male_booming",
  "Jaheira": "female_mature",
  "Viconia": "female_cool",
  "Edwin": "male_sardonic"
}
```

- Use absolute paths for reference audio files (voice cloning)
- Use Index-TTS preset names for built-in voices
- `_default_` is used when a speaker has no explicit mapping

---

## Step 2: Synthesize Audio

Run the synthesis script from the repository root:

```powershell
cd "C:\Users\tenod\source\repos\BG2 Voiceover"
python scripts/synth.py
```

**What it does:**
1. Reads `data/lines.csv` and `data/voices.json`
2. For each line, invokes Index-TTS CLI:
   ```
   indextts.exe -c checkpoints/config.yaml -v <voice> -o <output.wav> "<text>"
   ```
3. Outputs WAV files to `build/OGG/<StrRef>.wav`

**Output example:**
- `build/OGG/38606.wav` (mono, 16-bit, 22050 Hz, ~9.5 seconds)

**Note:** The first synthesis run may take extra time as Index-TTS initializes models.

---

## Step 3: Stage Audio for WeiDU

Copy synthesized files into the mod structure with the `OH` prefix:

```powershell
Copy-Item "build\OGG\38606.wav" "mod\vvoBG\OGG\OH38606.wav"
```

**Naming convention:**
- Game expects audio files named `OH<StrRef>.wav`
- WeiDU will copy these into the game's `override/` folder

---

## Step 4: Configure WeiDU Installer

### `mod/vvoBG.tp2`

Define the mod package:

```weidu
BACKUP ~vvoBG/backup~
AUTHOR ~BG2 Voiceover Automation~

BEGIN ~BG2 Voiceover: Imoen GOLEM line~

// Set strref 38606 to play audio OH38606
STRING_SET 38606 ~Wow, a golem. Powerful magic stuff. Odd that it's not hostile. I suppose its maker didn't expect us to escape, so it never got orders for restraining us.~ [OH38606]

// Copy audio into override
COPY ~vvoBG/OGG/OH38606.wav~ ~override/OH38606.wav~
```

**Key WeiDU commands:**
- `STRING_SET <strref> ~<text>~ [<audio>]`: Updates `dialog.tlk` to point strref to the audio file
- `COPY ~source~ ~destination~`: Copies audio into the game's override folder

---

## Step 5: Install Into BG2EE

### Copy Mod Files to Game Directory

```powershell
$GameDir = "E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition"
$RepoModDir = "C:\Users\tenod\source\repos\BG2 Voiceover\mod"

# Copy installer and TP2
Copy-Item "$RepoModDir\setup-vvoBG.exe" "$GameDir\"
Copy-Item "$RepoModDir\vvoBG.tp2" "$GameDir\"

# Copy mod folder
Copy-Item "$RepoModDir\vvoBG" "$GameDir\" -Recurse
```

### Run WeiDU Installer

From the game directory:

```powershell
cd "E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition"
.\setup-vvoBG.exe
```

**Installation prompts:**
```
Install Component [BG2 Voiceover: Imoen GOLEM line]?
[I]nstall, or [N]ot Install or [Q]uit? I
```

**Expected output:**
```
Installing [BG2 Voiceover: Imoen GOLEM line]
Copying 1 file ...
[.\lang\en_us\dialog.tlk] created, 104201 string entries
SUCCESSFULLY INSTALLED      BG2 Voiceover: Imoen GOLEM line
```

### Verify Installation

Check that the audio file was copied:

```powershell
Test-Path "E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition\override\OH38606.wav"
# Should return: True
```

---

## Step 6: Test In-Game

1. Launch BG2EE
2. Load a save or start a new game in **Irenicus's Dungeon** (Chapter 1)
3. Navigate to the area where you encounter the first golem
4. Trigger the dialogue where Imoen says:
   > "Wow, a golem. Powerful magic stuff..."
5. The synthesized audio should play

**Technical notes:**
- String reference 38606 corresponds to this specific Imoen line
- The game reads audio from `override/OH38606.wav`
- The updated `dialog.tlk` links the strref to the audio file

---

## Workflow Summary

```
1. Edit data/lines.csv (add StrRef, Speaker, Text)
2. Run scripts/synth.py → generates build/OGG/<StrRef>.wav
3. Copy to mod/vvoBG/OGG/OH<StrRef>.wav
4. Update mod/vvoBG.tp2 (add STRING_SET and COPY commands)
5. Copy mod files to BG2EE directory
6. Run setup-vvoBG.exe in game directory
7. Launch game and test
```

---

## Troubleshooting

### Index-TTS fails to synthesize

**Problem:** `indextts.exe` command fails or produces no output

**Solutions:**
- Verify Index-TTS is installed: `C:\Users\tenod\source\repos\TTS\index-tts\.venv\Scripts\indextts.exe --help`
- Check `checkpoints/config.yaml` exists and is valid
- Ensure reference audio files (e.g., `refs/imoen_ref.wav`) are present for cloned voices
- Review Python errors in the synthesis script output

### WeiDU installation fails

**Problem:** `setup-vvoBG.exe` reports "Not a game directory"

**Solutions:**
- Run the installer from the BG2EE root directory (where `Baldur.exe` is located)
- Verify `chitin.key` exists in the game directory
- Use absolute paths or navigate to the game folder first

### Audio doesn't play in-game

**Problem:** Line displays but no audio plays

**Solutions:**
- Verify `override/OH<StrRef>.wav` exists and is readable
- Check file format: mono, 16-bit PCM, 22050 Hz sample rate
- Ensure StrRef number matches the dialogue trigger
- Test with original BG2 audio files to confirm the game's audio system works

### Wrong voice plays

**Problem:** Audio plays but sounds incorrect

**Solutions:**
- Check `voices.json` mapping for the speaker
- Verify reference audio quality and format
- Re-synthesize with a different Index-TTS voice preset

---

## Adding New Lines

To voice additional dialogue:

1. **Find the StrRef:**
   - Use Near Infinity or WeiDU's `--tlk-string` to search `dialog.tlk`
   - Or extract from `BG2 Files/dialog.tra`

2. **Add to `data/lines.csv`:**
   ```csv
   12345,Minsc,"Go for the eyes, Boo! Go for the eyes!"
   ```

3. **Synthesize:**
   ```powershell
   python scripts/synth.py
   ```

4. **Stage for WeiDU:**
   ```powershell
   Copy-Item "build\OGG\12345.wav" "mod\vvoBG\OGG\OH12345.wav"
   ```

5. **Update `mod/vvoBG.tp2`:**
   ```weidu
   STRING_SET 12345 ~Go for the eyes, Boo! Go for the eyes!~ [OH12345]
   COPY ~vvoBG/OGG/OH12345.wav~ ~override/OH12345.wav~
   ```

6. **Reinstall:**
   - Uninstall previous version: `.\setup-vvoBG.exe --uninstall`
   - Reinstall: `.\setup-vvoBG.exe`

---

## Improving Voice Accuracy

### Using Better Reference Audio

The quality of synthesized voices depends heavily on the reference audio used for voice cloning. Here's how to improve accuracy:

#### 1. Use Multiple Reference Samples

Instead of a single reference file, concatenate multiple original character lines:

```powershell
python scripts/create_reference.py
```

**Why this helps:**
- Captures more voice characteristics (pitch variation, cadence, emotional range)
- Reduces impact of audio artifacts in any single file
- Gives Index-TTS more data to learn from

#### 2. Select Quality Reference Files

Choose original BG2 audio files that are:
- **Clear**: No background combat sounds or music
- **Varied**: Different emotions (neutral, happy, concerned, excited)
- **Diverse**: Mix of short and long sentences
- **Clean**: Minimal distortion or compression artifacts

**Recommended total duration:** 20-30 seconds (5-10 files)

#### 3. Find Character-Specific Audio

To identify which WAV files belong to a character:

1. **Cross-reference with `BG2 Files/dialog.tra`:**
   - Search for the character's name in dialog.tra
   - Note the StrRef numbers for their lines
   - Original audio files are named `OH<StrRef>.WAV`

2. **Common StrRef ranges** (BG2 Enhanced Edition):
   - Imoen: ~78715-79500 range (varied)
   - Minsc: ~79700-80300 range
   - Jaheira: ~80400-81000 range
   - Other companions follow similar patterns

3. **Listen and verify:**
   ```powershell
   # Play a file in Windows
   Start-Process "BG2 Files\WAV Files\OH78715.WAV"
   ```

#### 4. Create Enhanced Reference

Edit `scripts/create_reference.py` and add your selected files:

```python
imoen_strrefs = [
    "OH78715.WAV",  # Clear neutral dialogue
    "OH78720.WAV",  # Questioning tone
    "OH78725.WAV",  # Happy/excited
    "OH78730.WAV",  # Concerned
    "OH78735.WAV",  # Longer sentence
]
```

Then run:
```powershell
python scripts/create_reference.py
```

This creates `refs/imoen_ref_multi.wav` combining all selected files.

#### 5. Update Voice Mapping

Edit `data/voices.json`:

```json
{
  "_default_": "narrator",
  "Imoen": "C:\\Users\\tenod\\source\\repos\\BG2 Voiceover\\refs\\imoen_ref_multi.wav"
}
```

#### 6. Alternative: Try Index-TTS Presets

If reference audio quality is poor, test with built-in voices:

```json
{
  "Imoen": "female_youthful",
  "Minsc": "male_booming",
  "Jaheira": "female_mature"
}
```

Check Index-TTS documentation for available preset names.

#### 7. Iterative Refinement

1. Synthesize a test line with your reference
2. Compare to original BG2 audio
3. If quality is poor:
   - Try different reference file combinations
   - Ensure reference files are mono, 16-bit, 22050 Hz
   - Check for audio distortion in reference
4. Re-run synthesis pipeline

**Quality improvement tip:** Sometimes a shorter, clearer reference (10-15 seconds) works better than a longer one with varied quality.

---

## Credits

- **Index-TTS**: https://github.com/MLo7Ghinsan/iNDEX-tts
- **WeiDU**: https://weidu.org/
- **Baldur's Gate II**: Beamdog, BioWare, Black Isle Studios

---

## License

This project is a modding tool for Baldur's Gate II Enhanced Edition. Respect all applicable licenses for Index-TTS, WeiDU, and the game content.
