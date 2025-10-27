# Scripts Directory

Python automation tools for BG2 Voiceover project, organized by purpose.

## Directory Structure

### `core/` - Essential Workflow Scripts

Core scripts for the main synthesis and deployment workflow:

- **synth.py** - Main TTS synthesis script
  - `python scripts/core/synth.py --chapter 1` - Synthesize Chapter 1 dialogue
  - `python scripts/core/synth.py --input data/custom.csv` - Synthesize custom CSV

- **deploy.py** - Deploy WAV files to WeiDU mod structure
  - `python scripts/core/deploy.py --test --generate-tp2` - Deploy test files
  - `python scripts/core/deploy.py --chapter 1` - Deploy Chapter 1 files

- **convert_d_to_csv.py** - Convert Near Infinity .D exports to CSV
  - Parses dialogue state machine exports into structured CSV format

- **near_infinity_join.py** - Join Near Infinity exports with dialogue text
  - Merges dialogue structure with text content

### `voice_design/` - Voice Reference & Audition Tools

Tools for creating and testing voice presets:

- **audition.py** - Interactive voice audition system
  - Test different voice presets against character dialogue
  - Generate HTML audition reports

- **create_reference.py** - Create voice reference files
  - Extract audio samples from game files
  - Build multi-sample reference WAV for voice cloning

- **build_cards.py** - Generate character voice cards
  - Create character trait profiles from metadata

- **build_refs.py** - Suggest voice presets based on character traits
  - `python scripts/voice_design/build_refs.py --write` - Update voices.sample.json

### `utils/` - Helper & Monitoring Scripts

Utility scripts for testing and monitoring:

- **check_progress.py** - Monitor synthesis progress
  - `python scripts/utils/check_progress.py --chapter 1` - Check Chapter 1 progress
  - Non-blocking progress monitoring for long synthesis runs

- **verify_install.py** - Verify WeiDU mod installation
  - Check if mod files were correctly installed to game directory

- **test_audio.py** - Test audio file playback
  - Quick audio validation

- **preview_imoen_audio.py** - Preview Imoen voice samples
  - Test voice quality for Imoen reference files

### `stubs/` - Unimplemented/Experimental Scripts

Placeholder scripts not yet fully implemented:

- **gen_pseudorefs.py** - Generate pseudo-references (stub)
- **synth_cache.py** - Synthesis caching system (stub)
- **character_lib.py** - Character library management (stub)

## Usage Patterns

### Basic Workflow

```powershell
# 1. Synthesize dialogue
python scripts/core/synth.py --chapter 1

# 2. Monitor progress (in another terminal)
python scripts/utils/check_progress.py --chapter 1

# 3. Deploy to mod structure
python scripts/core/deploy.py --chapter 1 --generate-tp2

# 4. Verify installation
python scripts/utils/verify_install.py
```

### Voice Design Workflow

```powershell
# 1. Create character voice reference
python scripts/voice_design/create_reference.py

# 2. Build voice preset recommendations
python scripts/voice_design/build_refs.py --write

# 3. Audition voices for character
python scripts/voice_design/audition.py
```

## Notes

- All scripts use `Path(__file__).resolve().parents[2]` to find project root
- Scripts depend on `src/bg2vo/` package for shared functionality
- Configuration loaded from `config/defaults.yaml`
- Most scripts support `--help` flag for usage information

## Development

When adding new scripts:

1. Place in appropriate subdirectory based on purpose
2. Use `ROOT = Path(__file__).resolve().parents[2]` for path resolution
3. Import bg2vo modules: `from bg2vo.config import load_config`
4. Add `--help` argument for documentation
5. Update this README with script description
