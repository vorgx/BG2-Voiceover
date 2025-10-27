# Agent Responsibilities

This document provides operational guidelines for AI agents working on this repository, including where new files should be placed.

## Mission
- Maintain the BG2 voiceover pipeline from raw exports through WeiDU installation.
- Ensure sanitization scripts and synthesis tooling remain functional.
- Introduce blueprint enhancements without disrupting existing Chapter 1 workflows.

## Key References
- `docs/workflows/COMPLETE_WORKFLOW.md`: **Complete end-to-end workflow documentation** - the definitive guide for the entire synthesis pipeline from data collection through packaging.
- `docs/getting-started/CHAPTER_PIPELINE.md`: chapter-by-chapter checklist.
- `docs/reference/ARCHITECTURE.md`: repository structure and data flow.
- `docs/guides/`: how-to guides for specific tasks.

---

## File Placement Guidelines

### Where to Put New Files

#### **Scripts** → `scripts/`

Place new Python scripts in the appropriate subdirectory:

- **`scripts/core/`** - Essential workflow scripts
  - Synthesis, deployment, data conversion
  - Examples: synth.py, deploy.py, convert_d_to_csv.py
  - **Add here if**: Script is part of main Chapter N workflow

- **`scripts/voice_design/`** - Voice reference & audition tools
  - Voice creation, testing, and preset management
  - Examples: audition.py, create_reference.py, build_refs.py
  - **Add here if**: Script helps design/test voices for characters

- **`scripts/utils/`** - Helper & monitoring scripts
  - Progress monitoring, verification, testing
  - Examples: check_progress.py, verify_install.py, test_audio.py
  - **Add here if**: Script is a utility/helper tool

- **`scripts/stubs/`** - Experimental/incomplete scripts
  - Not yet fully implemented or documented
  - Examples: gen_pseudorefs.py, synth_cache.py
  - **Add here if**: Script is experimental or work-in-progress

**Important**: All scripts must use `ROOT = Path(__file__).resolve().parents[2]` to find project root.

#### **Documentation** → `docs/`

Place new documentation in the appropriate subdirectory:

- **`docs/getting-started/`** - Quickstart & workflow guides
  - Current status, integration testing, pipeline workflows
  - **Add here if**: Doc helps someone get started or understand current state

- **`docs/guides/`** - How-to guides
  - Step-by-step instructions for specific tasks
  - Examples: voice config, character setup, audition process
  - **Add here if**: Doc explains HOW to do something specific

- **`docs/reference/`** - Technical reference
  - Architecture, API docs, presets, testing procedures
  - **Add here if**: Doc explains technical details or serves as reference

- **`docs/dev/`** - Development & contributing
  - This file, development guidelines, Near Infinity tools
  - **Add here if**: Doc is for contributors/developers

#### **Data Files** → `data/` (active only)

- **Active datasets**: lines.csv, voices.json, characters.csv, chapterN_lines.csv
- **Chapter splits**: chapter1_split/, chapter2_split/, etc.
- **Metadata**: chapterN_targets.csv

**DO NOT add**: Analysis outputs, temporary files, experimental CSVs
→ Those go to `archive/data/` if they need to be kept

#### **Configuration** → `config/`

- **Templates**: voices.sample.json (staging/experimentation)
- **Defaults**: defaults.yaml (system paths and settings)

**Production config**: `data/voices.json` (not in config/)

#### **Source Code** → `src/bg2vo/`

Python package modules only:
- Core functionality used by multiple scripts
- Examples: config.py, lines.py, voices.py, audit.py

#### **Tests** → `tests/`

All pytest test files.

#### **Build Outputs** → `build/`

Generated audio files (OGG/, split/, etc.)

#### **Historical/Archive** → `archive/`

- Planning documents no longer actively used
- Old analysis CSVs that can be regenerated
- Superseded documentation

**Never add new files here** - archive is for moving old files only.

---

## Agent Playbook

### 1. Starting Work
- **Read `docs/workflows/COMPLETE_WORKFLOW.md` first** - this is the comprehensive guide covering all 10 stages of the pipeline with exact commands, file locations, and troubleshooting.
- Check `docs/getting-started/INTEGRATION_STATUS.md` for current state
- Review `docs/getting-started/CHAPTER_PIPELINE.md` for workflow checklist
- Consult relevant guides in `docs/guides/` for specific tasks

### 2. Creating New Scripts
```python
# Template for new scripts:
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]  # Project root
sys.path.insert(0, str(ROOT / "src"))

from bg2vo.config import load_config
from bg2vo.lines import load_lines
# ... rest of imports
```

**Then**:
1. Place script in appropriate `scripts/` subdirectory
2. Update `scripts/README.md` with script description
3. Add `--help` argument for documentation
4. Test thoroughly
5. Document usage in relevant guide

### 3. Creating New Documentation
1. Determine category (getting-started, guides, reference, or dev)
2. Create markdown file in appropriate subdirectory
3. Update parent directory README if needed
4. Use relative links for cross-references:
   - Same directory: `[text](FILE.md)`
   - Parent: `[text](../FILE.md)`
   - Other subdir: `[text](../other-dir/FILE.md)`

### 4. Adding Test Data
- **Active workflow data** → `data/`
- **Analysis output** → Run once, verify, then move to `archive/data/`
- **Temporary test files** → Use temp directory or build/, clean up after

### 5. Before Committing
- Run `pytest tests/` (ensure 4/4 passing)
- Test key scripts: `synth.py --help`, `check_progress.py --help`, `deploy.py --help`
- Verify no broken doc links
- Update relevant documentation

---

## Common Patterns

### Pattern: Adding a Chapter N Workflow Script
```
1. Create: scripts/core/process_chapterN.py
2. Use: ROOT = Path(__file__).resolve().parents[2]
3. Import: from bg2vo.config import load_config
4. Document: Update scripts/README.md
5. Test: python scripts/core/process_chapterN.py --help
```

### Pattern: Adding a Voice Tool
```
1. Create: scripts/voice_design/new_tool.py
2. Follow: Same ROOT pattern as above
3. Document: Create docs/guides/NEW_TOOL_GUIDE.md
4. Test: With sample data
```

### Pattern: Adding Analysis Scripts
```
1. Create: scripts/utils/analyze_something.py
2. Output: to build/ or temp location
3. Archive: Move valuable outputs to archive/data/ after review
```

---

## Tool Preferences

**For Python execution:**
- ✅ `mcp_pylance_mcp_s_pylanceRunCodeSnippet` (preferred - clean output, no shell issues)
- ⚠️ `run_in_terminal` (only when subprocess interaction needed)

**For file operations:**
- ✅ `create_file` for new files
- ✅ `replace_string_in_file` for targeted edits
- ✅ `read_file` to verify before editing

**For testing:**
- ✅ Always run `pytest tests/` after structural changes
- ✅ Test scripts with `--help` after moving/creating
- ✅ Verify doc links after restructuring

---

## Complete Workflow Overview

For the full detailed workflow, see `docs/workflows/COMPLETE_WORKFLOW.md`.

**Quick Reference - 10 Stage Pipeline:**

1. **Data Collection** - Gather WeiDU files, voice references, emotion prompts
2. **Database Building** - `build_complete_lines_db.py` → `data/all_lines.csv`
3. **Data Cleaning** - `clean_placeholders.py` + `split_chapters.py`
4. **Voice Configuration** - `map_chapter1_speakers.py` + lock voices in `voices.json`
5. **Target Generation** - `filter_chapter1_for_synth.py` → `chapter1_unvoiced_only.csv`
6. **Batch Synthesis** - `synth_batch.py` using Index-TTS `.venv` → `build/OGG/*.wav`
7. **Verification** - Re-run filter scripts to confirm 0 gaps
8. **Quality Assurance** - Manual listening and adjustments
9. **Packaging** - `deploy.py` → `mod/vvoBG/`
10. **Iteration** - Repeat for next chapters

**Critical Command:**
```powershell
C:/Users/tenod/source/repos/TTS/index-tts/.venv/Scripts/python.exe scripts/core/synth_batch.py --input data/chapter1_unvoiced_only.csv
```

---

## Workflows

### Complete Chapter Workflow

1. **Export from Game**
   - Use Near Infinity to export dialogue files
   - See `../guides/NEAR_INFINITY_EXPORT_STEPS.md`

2. **Convert to CSV**
   ```powershell
   python scripts/core/convert_d_to_csv.py
   python scripts/core/near_infinity_join.py
   ```

3. **Configure Voices**
   - Update `data/voices.json` with character voice mappings
   - Create reference files if needed: `python scripts/voice_design/create_reference.py`
   - See `../guides/VOICES_JSON_GUIDE.md`

4. **Synthesize Audio**
   ```powershell
   # Synthesize chapter dialogue
   python scripts/core/synth.py --chapter 1
   
   # Monitor progress (in another terminal)
   python scripts/utils/check_progress.py --chapter 1
   ```

5. **Deploy to Mod**
   ```powershell
   # Deploy and generate TP2 entries
   python scripts/core/deploy.py --chapter 1 --generate-tp2
   ```

6. **Install to Game**
   ```powershell
   # Copy mod files to game directory
   Copy-Item mod/setup-vvoBG.exe "E:\SteamLibrary\...\Baldur's Gate II Enhanced Edition\"
   Copy-Item mod/vvoBG.tp2 "E:\SteamLibrary\...\Baldur's Gate II Enhanced Edition\"
   Copy-Item mod/vvoBG "E:\SteamLibrary\...\Baldur's Gate II Enhanced Edition\" -Recurse
   
   # Run WeiDU installer
   cd "E:\SteamLibrary\...\Baldur's Gate II Enhanced Edition"
   .\setup-vvoBG.exe
   ```

7. **Test In-Game**
   - Launch BG2EE
   - Load save or start in relevant chapter
   - Trigger dialogue to verify audio plays

---

## Data Flow Pipelines

### Synthesis Pipeline

```
data/lines.csv           → Input: StrRef, Speaker, Text
    ↓
data/voices.json         → Voice mapping: Speaker → Index-TTS voice/reference
    ↓
scripts/core/synth.py    → Invokes Index-TTS for each line
    ↓
build/OGG/<StrRef>.wav   → Generated audio (e.g., 38606.wav)
```

### Packaging Pipeline

```
build/OGG/<StrRef>.wav              → Generated audio
    ↓
scripts/core/deploy.py              → Copies and renames
    ↓
mod/vvoBG/OGG/OH<StrRef>.wav        → Staged for WeiDU (OH prefix added)
    ↓
mod/vvoBG.tp2                       → TP2 entries generated (STRING_SET + COPY)
```

### Installation Pipeline

```
mod/setup-vvoBG.exe + vvoBG.tp2 + vvoBG/  → Copied to game directory
    ↓
setup-vvoBG.exe (executed)                → WeiDU installer runs
    ↓
override/OH<StrRef>.wav                   → Audio installed to game
    +
lang/en_us/dialog.tlk                     → String table updated
```

---

## Environment Paths (Reference)

See archived `agent.md` for detailed environment setup. Key paths:

- **Index-TTS**: `C:\Users\tenod\source\repos\TTS\index-tts`
- **BG2EE**: `E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition`
- **Repository**: `C:\Users\tenod\source\repos\BG2 Voiceover`

---

## Questions & Clarifications

When uncertain about file placement:
1. Check this guide first
2. Look at similar existing files for precedent
3. Review `scripts/README.md` or `docs/` structure
4. When in doubt, ask the user

**Golden Rule**: Keep active workflow files separate from archives, experiments separate from production.

