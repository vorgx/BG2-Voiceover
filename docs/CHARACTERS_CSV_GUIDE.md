# characters.csv - Character Voice Library

## Overview

Central tracking system for all BG2EE characters requiring voice synthesis. Prevents voice drift, documents decisions, and prioritizes work.

## Purpose

1. **Track Progress**: See which characters are done vs pending
2. **Document Choices**: Record voice selections and rationale
3. **Prevent Drift**: Maintain consistent voice characteristics across sessions
4. **Prioritize Work**: Focus on high-value characters first
5. **Quality Control**: Ensure voice matches character archetype

## File Location

`data/characters.csv`

## Field Reference

### Identity Fields

#### `Canonical` (string)
Primary character name used throughout project.
- Use proper capitalization (e.g., "Imoen" not "IMOEN")
- Consistent with voices.json keys

#### `Aliases` (string, semicolon-separated)
Alternate names/spellings found in game files.
- Example: `IMOEN;IMOEN2`
- Helps locate files during bulk export

#### `DLGFiles` (string, pipe-separated)
Dialog files associated with this character.
- Format: `FILENAME.DLG|FILENAME2.DLG`
- Example: `MINSC.DLG|MINSCJ.DLG`
- Used by Near Infinity export process

### Voice Coverage

#### `HasCanonicalVoice` (enum)
Extent of existing voice acting.
- **None**: No voice acting at all
- **Partial**: Some lines voiced (selection sounds, battle cries)
- **Full**: Complete voice coverage

**Why it matters**: Partial = can extract reference audio

### Character Description

#### `Gender` (M/F)
Biological sex for voice selection.

#### `AgeBand` (enum)
Age category affects voice timbre.
- **Young**: Teen/early 20s (Imoen, Aerie)
- **Adult**: 25-45 (Minsc, Viconia, Edwin)
- **Mature**: 45+ (Jaheira, Keldorn)

#### `Accent` (string)
Regional or ethnic accent characteristics.
- **Neutral**: Standard/American
- **Drow**: Dark elf inflection
- **Scottish**: Korgan
- **Upper-class**: British noble
- **Theatrical**: Shakespearean
- **Asian-inspired**: Eastern influence

#### `Archetype` (string)
Personality/role archetype.

**Common archetypes:**
- Cheery, Stern, Sardonic, Arrogant
- Timid, Aggressive, Conflicted, Righteous
- Idealist, Poetic, Philosophical, Heroic
- Stoic, Charming, Menacing

#### `Energy` (enum)
Vocal energy level.
- **VeryHigh**: Enthusiastic, excitable (Minsc)
- **High**: Energetic, active (Imoen, Mazzy)
- **Medium**: Balanced (most characters)
- **Low**: Subdued, calm (Cernd, Valygar)

#### `Timbre` (string)
Voice quality/texture.

**Common timbres:**
- Bright, Mature, Cool, Boomy, Sardonic
- Gentle, Gruff, Noble, Wise, Light
- Smooth, Deep, Strong, Flat, Menacing

### Implementation

#### `Notes` (string)
Character-specific context, quirks, or special considerations.
- Example: "Has iconic catchphrase"
- Example: "Internal monologue asides"
- Example: "Hamster references"

#### `VoicePreset` (string)
Index-TTS preset name if used.
- See: docs/VOICES_JSON_GUIDE.md for available presets
- Leave empty if using only custom reference

#### `RefFile` (string, path)
Path to custom reference audio file.
- Relative to project root: `refs/character_ref_multi.wav`
- Leave empty if using only preset

#### `Status` (enum)
Current state of voice implementation.

**Status values:**
- **Draft**: Character defined, no voice work started
- **Pending**: Character ready for voice work
- **Auditioned**: 2-3 variants tested, choice made
- **Locked**: Voice finalized and quality-approved

**Workflow:**
```
Draft → Pending → Auditioned → Locked
```

## Usage Workflow

### 1. Add New Character

```csv
Sarevok,SAREVOK,SAREVOK.DLG,Partial,M,Adult,Neutral,Menacing,Low,Deep,Former villain - dark and brooding,male_menacing,,Draft
```

### 2. Promote to Pending

When ready to work on character:
```csv
Status: Draft → Pending
```

Add notes about voice direction.

### 3. Create Voice Options

For preset-based:
```csv
VoicePreset: male_menacing
Status: Pending → Auditioned
```

For reference-based:
1. Find source audio files
2. Create multi-reference
3. Update RefFile path
```csv
RefFile: refs/sarevok_ref_multi.wav
Status: Pending → Auditioned
```

### 4. Test and Lock

After synthesis and quality check:
```csv
Status: Auditioned → Locked
```

Once locked, voice should not change without good reason.

## Priority Guidelines

### Phase 1: Core Companions (High Priority)
Characters present for most of game:
- ✅ Imoen (Locked)
- ⏳ Minsc (Pending)
- ⏳ Jaheira (Pending)
- ⏳ Viconia (Pending)
- ⏳ Edwin (Pending)

### Phase 2: Recruitable NPCs (Medium Priority)
Optional but common companions:
- Aerie, Korgan, Anomen, Keldorn, Nalia
- Haer'Dalis, Cernd, Mazzy, Valygar

### Phase 3: Story Characters (Lower Priority)
Important but less dialogue:
- Yoshimo, Sarevok
- Quest givers, merchants

### Phase 4: Minor NPCs (As Needed)
Background characters, one-off encounters.

## Quality Checklist

Before marking **Locked**, verify:

- [ ] Voice matches gender and age
- [ ] Energy level appropriate to personality
- [ ] Timbre distinct from similar characters
- [ ] Accent consistent (if applicable)
- [ ] Test synthesis sounds natural
- [ ] In-game validation confirms quality

## Analysis Queries

### PowerShell Examples:

**Count by status:**
```powershell
Import-Csv "data\characters.csv" | Group-Object Status | Select-Object Name, Count
```

**Show pending work:**
```powershell
Import-Csv "data\characters.csv" | Where-Object {$_.Status -eq "Pending"} | Format-Table Canonical, VoicePreset, RefFile
```

**List characters needing references:**
```powershell
Import-Csv "data\characters.csv" | Where-Object {$_.RefFile -eq "" -and $_.Status -ne "Draft"} | Select-Object Canonical, Archetype, Energy
```

**Find high-energy characters:**
```powershell
Import-Csv "data\characters.csv" | Where-Object {$_.Energy -match "High"} | Select-Object Canonical, Energy, Timbre
```

## Integration with Other Files

### voices.json
When character moves to **Auditioned** or **Locked**, update voices.json:

**From characters.csv:**
```csv
Minsc,MINSC,MINSC.DLG,Partial,M,Adult,Neutral,Boisterous,VeryHigh,Boomy,...,male_booming,refs/minsc_ref_multi.wav,Locked
```

**To voices.json:**
```json
{
  "Minsc": {
    "voice": "male_booming",
    "ref": "refs/minsc_ref_multi.wav",
    "emo_alpha": 1.0
  }
}
```

### lines.csv
Speaker names in lines.csv must match `Canonical` field:

**characters.csv:**
```
Canonical: Imoen
```

**lines.csv:**
```
StrRef,Speaker,Text
38606,Imoen,"Wow, a golem..."
```

### Near Infinity Export
Use `Aliases` and `DLGFiles` to find source files:

```powershell
# Get character info
$char = Import-Csv "data\characters.csv" | Where-Object {$_.Canonical -eq "Minsc"}

# Export their DLG files
$dlgFiles = $char.DLGFiles -split '\|'
# Process each file in Near Infinity...
```

## Best Practices

### DO:
✅ Update status as work progresses
✅ Document voice decisions in Notes
✅ Lock voices after quality approval
✅ Keep Canonical names consistent across files
✅ Prioritize high-value characters
✅ Review similar characters for uniqueness

### DON'T:
❌ Change locked voices without reason
❌ Use inconsistent name capitalization
❌ Skip archetype/energy documentation
❌ Leave status as Draft indefinitely
❌ Forget to update voices.json after locking

## Example: Complete Workflow

### Starting State (Draft):
```csv
Minsc,MINSC,MINSC.DLG|MINSCJ.DLG,Partial,M,Adult,Neutral,Boisterous,VeryHigh,Boomy,Ranger with hamster,male_booming,,Draft
```

### Step 1: Promote to Pending
```csv
...,Draft → Pending
```

### Step 2: Create Multi-Reference
1. Find MINSC*.WAV files
2. Select 7 diverse samples (heroic, confused, angry)
3. Run create_reference.py
4. Output: refs/minsc_ref_multi.wav

### Step 3: Update CSV
```csv
...,male_booming,refs/minsc_ref_multi.wav,Pending → Auditioned
```

### Step 4: Test Synthesis
1. Add test line to lines.csv
2. Run synthesis
3. Listen and validate quality

### Step 5: Lock
```csv
...,refs/minsc_ref_multi.wav,Auditioned → Locked
```

### Step 6: Update voices.json
```json
{
  "Minsc": {
    "voice": "male_booming",
    "ref": "refs/minsc_ref_multi.wav"
  }
}
```

---

## Current Status Summary

**Total Characters:** 16
- **Locked:** 1 (Imoen)
- **Pending:** 4 (Minsc, Jaheira, Viconia, Edwin)
- **Draft:** 11 (remaining companions)

**Next Actions:**
1. Complete Phase 1 (4 pending characters)
2. Create multi-references for each
3. Test and lock voices
4. Move to Phase 2

---

**Version:** 1.0  
**Updated:** October 26, 2025  
**Status:** Production-ready tracking system
