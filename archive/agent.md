# Agent Configuration & Requirements

## Overview

This document describes the AI agent configuration and required settings to successfully work with the BG2 Voiceover Automation project.

---

## Required Environment Settings

### 1. Index-TTS Configuration

**Installation Path:**
```
C:\Users\tenod\source\repos\TTS\index-tts
```

**Virtual Environment:**
- Location: `C:\Users\tenod\source\repos\TTS\index-tts\.venv`
- Activation command: `.venv\Scripts\Activate.ps1` (PowerShell)
- Python executable: `.venv\Scripts\python.exe`

**Checkpoints:**
- Location: `C:\Users\tenod\source\repos\TTS\index-tts\checkpoints`
- Required files:
  - `config.yaml` - Index-TTS configuration
  - Model checkpoint files (downloaded during Index-TTS setup)

**CLI Executable:**
- Path: `C:\Users\tenod\source\repos\TTS\index-tts\.venv\Scripts\indextts.exe`
- Invoked by `scripts/synth.py` with subprocess module

### 2. BG2EE Game Installation

**Game Directory:**
```
E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition
```

**Key Files:**
- `Baldur.exe` - Game executable
- `chitin.key` - Resource index (required for WeiDU detection)
- `lang\en_us\dialog.tlk` - Dialogue string table (modified by WeiDU)
- `override\` - Directory for mod overrides

### 3. Repository Structure

**Project Root:**
```
C:\Users\tenod\source\repos\BG2 Voiceover
```

**Critical Directories:**
- `data/` - Input data (lines.csv, voices.json)
- `scripts/` - Python automation scripts
- `build/OGG/` - Generated audio output (StrRef.wav format)
- `mod/vvoBG/OGG/` - Staged audio for WeiDU (OHStrRef.wav format)
- `refs/` - Reference audio for voice cloning

---

## Python Environment

### Dependencies

The project uses Python 3.10+ with the following requirements:

```python
# No external packages required for core synthesis
# synth.py uses only standard library: subprocess, csv, json, pathlib
```

### Running Python Scripts

**From Repository Root:**
```powershell
cd "C:\Users\tenod\source\repos\BG2 Voiceover"
python scripts/synth.py
```

**Note:** The agent should use the system Python, not the Index-TTS venv, to run `synth.py`. The script invokes Index-TTS via subprocess with absolute paths.

---

## Audio Format Specifications

### Generated Audio Requirements

All synthesized audio must meet BG2EE specifications:

- **Format:** WAV (RIFF)
- **Channels:** Mono (1 channel)
- **Bit Depth:** 16-bit PCM
- **Sample Rate:** 22050 Hz
- **Naming:** `OH<StrRef>.wav` (e.g., `OH38606.wav`)

### Index-TTS Output

Index-TTS produces audio matching these specs by default when using:
```bash
indextts.exe -c checkpoints/config.yaml -v <voice> -o <output.wav> "<text>"
```

**Verification Command:**
```powershell
# Check audio properties
Get-Item "build\OGG\38606.wav" | Select-Object Name, Length
```

---

## WeiDU Configuration

### Setup Files

**WeiDU Installer Stub:**
- File: `mod/setup-vvoBG.exe`
- Version: 24900 (or later)
- Purpose: Self-extracting installer for mod deployment

**TP2 Script:**
- File: `mod/vvoBG.tp2`
- Format: WeiDU scripting language
- Contains:
  - `BACKUP` directive (backup location)
  - `AUTHOR` metadata
  - `BEGIN` component definitions
  - `STRING_SET` commands (update dialog.tlk)
  - `COPY` commands (deploy audio files)

### Installation Process

**Required Files at Game Root:**
```
E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition\
├── setup-vvoBG.exe        # WeiDU installer
├── vvoBG.tp2              # Mod definition
└── vvoBG\                 # Mod folder
    └── OGG\               # Audio assets
        └── OH38606.wav    # Example audio
```

**Execution:**
```powershell
cd "E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition"
.\setup-vvoBG.exe
```

**Expected Behavior:**
- Detects `chitin.key` to confirm game directory
- Prompts: `[I]nstall, or [N]ot Install or [Q]uit?`
- On install: copies audio to `override/`, updates `dialog.tlk`
- Outputs: `SUCCESSFULLY INSTALLED`

---

## Agent Tool Usage Guidelines

### File Operations

**Reading Files:**
- Use `read_file` for structured data: `data/lines.csv`, `data/voices.json`, `mod/vvoBG.tp2`
- Use `list_dir` to verify directory structure

**Creating/Editing Files:**
- Use `create_file` for new Python scripts or config files
- Use `replace_string_in_file` for targeted edits to existing files (e.g., adding lines to TP2)

### Terminal Commands

**Shell:** PowerShell 5.1 (Windows)

**Common Operations:**
```powershell
# Copy files
Copy-Item "source.wav" "destination.wav"

# Copy directories recursively
Copy-Item "mod\vvoBG" "E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition\" -Recurse

# Check file existence
Test-Path "override\OH38606.wav"

# Run Python scripts
python scripts\synth.py

# Run WeiDU installer
.\setup-vvoBG.exe
```

**Notes:**
- Use `;` to chain commands on one line
- Prefer absolute paths to avoid navigation issues
- Use `-Recurse` flag for directory copies

### Python Execution

**Preferred Tool:** `mcp_pylance_mcp_s_pylanceRunCodeSnippet`

**Why:**
- Uses workspace Python interpreter
- No shell escaping issues
- Clean output formatting
- Direct memory execution (no temp files)

**Example Usage:**
```python
# Verify Index-TTS executable
import pathlib
indextts_path = pathlib.Path(r"C:\Users\tenod\source\repos\TTS\index-tts\.venv\Scripts\indextts.exe")
print(f"Index-TTS exists: {indextts_path.exists()}")
```

---

## Critical Path Information

### Synthesis Pipeline

1. **Input:** `data/lines.csv` (StrRef, Speaker, Text)
2. **Voice Mapping:** `data/voices.json` (Speaker → Index-TTS voice)
3. **Synthesis:** `scripts/synth.py` invokes `indextts.exe`
4. **Output:** `build/OGG/<StrRef>.wav`

### Packaging Pipeline

1. **Staging:** Copy `build/OGG/<StrRef>.wav` → `mod/vvoBG/OGG/OH<StrRef>.wav`
2. **TP2 Update:** Add `STRING_SET` and `COPY` commands to `mod/vvoBG.tp2`
3. **Deployment:** Copy `setup-vvoBG.exe`, `vvoBG.tp2`, and `vvoBG/` to game directory

### Installation Pipeline

1. **Execution:** Run `setup-vvoBG.exe` from game root
2. **WeiDU Actions:**
   - Copy `vvoBG/OGG/OH<StrRef>.wav` → `override/OH<StrRef>.wav`
   - Update `lang/en_us/dialog.tlk` with string reference mappings
3. **Verification:** Check `override/` for audio files

---

## Testing Procedures

### 1. Verify Index-TTS Installation

```powershell
C:\Users\tenod\source\repos\TTS\index-tts\.venv\Scripts\indextts.exe --help
```

**Expected Output:** Index-TTS CLI help text

### 2. Test Single Line Synthesis

```powershell
cd "C:\Users\tenod\source\repos\BG2 Voiceover"
python scripts/synth.py
```

**Expected Output:**
- `Synthesizing line 38606 (Imoen): Wow, a golem...`
- `build/OGG/38606.wav` created (~421 KB)

### 3. Verify Audio Format

```powershell
# PowerShell verification
Get-Item "build\OGG\38606.wav" | Select-Object Name, Length

# Or use Python snippet
import wave
with wave.open(r"build\OGG\38606.wav", 'rb') as wav:
    print(f"Channels: {wav.getnchannels()}, Sample Rate: {wav.getframerate()}, Bit Depth: {wav.getsampwidth()*8}")
```

**Expected:** Channels: 1, Sample Rate: 22050, Bit Depth: 16

### 4. Stage Audio for WeiDU

```powershell
Copy-Item "build\OGG\38606.wav" "mod\vvoBG\OGG\OH38606.wav"
Test-Path "mod\vvoBG\OGG\OH38606.wav"
```

**Expected:** `True`

### 5. Deploy to Game Directory

```powershell
$GameDir = "E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition"
Copy-Item "mod\setup-vvoBG.exe" "$GameDir\"
Copy-Item "mod\vvoBG.tp2" "$GameDir\"
Copy-Item "mod\vvoBG" "$GameDir\" -Recurse

Test-Path "$GameDir\setup-vvoBG.exe"
Test-Path "$GameDir\vvoBG.tp2"
Test-Path "$GameDir\vvoBG\OGG\OH38606.wav"
```

**Expected:** All return `True`

### 6. Run WeiDU Installer

```powershell
cd "E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition"
.\setup-vvoBG.exe
```

**User Input:** Type `I` and press Enter

**Expected Output:**
```
Installing [BG2 Voiceover: Imoen GOLEM line]
Copying 1 file ...
[.\lang\en_us\dialog.tlk] created, 104201 string entries
SUCCESSFULLY INSTALLED      BG2 Voiceover: Imoen GOLEM line
```

### 7. Verify Installation

```powershell
Test-Path "E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition\override\OH38606.wav"
```

**Expected:** `True`

### 8. In-Game Testing

1. Launch BG2EE
2. Load save or start new game in Irenicus's Dungeon
3. Navigate to golem encounter area
4. Trigger Imoen dialogue about the golem (StrRef 38606)
5. **Expected:** Synthesized voice plays: "Wow, a golem. Powerful magic stuff..."

---

## Common Issues & Solutions

### Issue: Index-TTS Not Found

**Symptom:** `FileNotFoundError: [Errno 2] No such file or directory: 'indextts.exe'`

**Solution:**
- Verify Index-TTS venv path in `scripts/synth.py`
- Update `INDEXTTS_EXE` variable to absolute path:
  ```python
  INDEXTTS_EXE = r"C:\Users\tenod\source\repos\TTS\index-tts\.venv\Scripts\indextts.exe"
  ```

### Issue: WeiDU "Not a game directory"

**Symptom:** `setup-vvoBG.exe` refuses to run

**Solution:**
- Navigate to game directory before running installer
- Verify `chitin.key` exists in the directory
- Do not run from repository; copy files to game root first

### Issue: Audio Doesn't Play In-Game

**Symptom:** Dialogue text displays but no audio

**Solutions:**
1. Check file naming: must be `OH<StrRef>.wav` (not `<StrRef>.wav`)
2. Verify audio format: mono, 16-bit, 22050 Hz
3. Confirm `override/OH38606.wav` exists and is readable
4. Check `dialog.tlk` was updated (file size should increase)
5. Ensure StrRef matches the actual in-game dialogue trigger

### Issue: Wrong Voice/Speaker

**Symptom:** Audio plays but sounds incorrect

**Solutions:**
1. Review `data/voices.json` speaker mapping
2. Verify reference audio path is correct and file exists
3. Try a different Index-TTS preset voice
4. Re-synthesize with updated voice configuration

---

## Agent Memory Checklist

When working on this project, the agent should be aware of:

- ✓ Index-TTS is at `C:\Users\tenod\source\repos\TTS\index-tts`
- ✓ BG2EE is at `E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition`
- ✓ Repository is at `C:\Users\tenod\source\repos\BG2 Voiceover`
- ✓ Generated audio goes to `build/OGG/<StrRef>.wav`
- ✓ Staged audio goes to `mod/vvoBG/OGG/OH<StrRef>.wav`
- ✓ Installed audio goes to `override/OH<StrRef>.wav` in game directory
- ✓ WeiDU requires execution from game root directory
- ✓ Audio format: mono, 16-bit PCM, 22050 Hz WAV
- ✓ String reference 38606 is Imoen's golem line (test case)
- ✓ Use `mcp_pylance_mcp_s_pylanceRunCodeSnippet` for Python verification
- ✓ Use PowerShell 5.1 syntax for terminal commands
- ✓ TP2 uses `STRING_SET` to link strrefs to audio files
- ✓ TP2 uses `COPY` to deploy audio to override folder

---

## Future Automation Considerations

### Batch Processing

To voice multiple lines efficiently:

1. **Auto-Staging Script:** Rename `build/OGG/*.wav` → `mod/vvoBG/OGG/OH*.wav`
2. **TP2 Generation:** Parse `data/lines.csv` to generate all `STRING_SET` and `COPY` commands
3. **Incremental Updates:** Only re-synthesize changed lines

### Quality Assurance

1. **Audio Validation:** Check format, duration, and quality metrics
2. **Reference Mapping:** Verify speaker-to-voice assignments
3. **In-Game Testing:** Automated trigger checks (if possible with scripting mods)

---

## Version History

- **v1.0** (2025-10-26): Initial configuration document
  - Confirmed working pipeline for single-line synthesis (StrRef 38606)
  - Documented Index-TTS integration, WeiDU packaging, BG2EE installation
  - Verified in-game audio playback

---

## Agent Tool Preferences

**For this project, prefer:**
- `mcp_pylance_mcp_s_pylanceRunCodeSnippet` over `run_in_terminal` for Python code
- `create_file` for new data files (CSV, JSON, TP2)
- `replace_string_in_file` for targeted edits (adding lines to existing TP2)
- `read_file` to verify file contents before editing
- Absolute paths in all operations to avoid navigation issues

**Avoid:**
- Creating temp files when direct execution is possible
- Running `python -c "..."` in terminal (escaping issues)
- Editing files manually via terminal commands (use file edit tools)
- Assuming file locations (always verify with `Test-Path` or `list_dir`)
