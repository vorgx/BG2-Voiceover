# Scaling Plan: Voice Synthesis for All Companions

## Overview

Apply proven multi-reference workflow to all BG2EE companion characters. Estimated completion: 8-12 hours of synthesis time + 2-3 hours setup/validation.

---

## Phase 1: Core Party Members (Priority)

### 1. Minsc
**Character**: Male ranger, booming heroic voice
**Current**: Using preset "male_booming"
**Goal**: Custom multi-reference from original voice files

**Action Items:**
- [ ] Search dialog.tra for Minsc lines
- [ ] Find MINSC##.WAV files in BG2 Files/WAV Files
- [ ] Select 5-10 samples (~20-30s total):
  - Heroic battle cries
  - Hamster references (iconic)
  - Determined/brave lines
  - Confused/simple-minded moments
  - Angry/threatening statements
- [ ] Update create_reference.py with Minsc files
- [ ] Generate minsc_ref_multi.wav
- [ ] Update voices.json

**Estimated Time**: 30-45 minutes

---

### 2. Jaheira
**Character**: Female druid, mature authoritative voice
**Current**: Using preset "female_mature"
**Goal**: Custom multi-reference from original voice files

**Action Items:**
- [ ] Search dialog.tra for Jaheira lines
- [ ] Find JAHEIRA##.WAV files
- [ ] Select 5-10 samples (~20-30s total):
  - Wise/mature advice
  - Nature-themed statements
  - Stern warnings
  - Caring/protective moments
  - Disapproving remarks
- [ ] Update create_reference.py with Jaheira files
- [ ] Generate jaheira_ref_multi.wav
- [ ] Update voices.json

**Estimated Time**: 30-45 minutes

---

### 3. Viconia
**Character**: Female drow, cool sardonic voice
**Current**: Using preset "female_cool"
**Goal**: Custom multi-reference from original voice files

**Action Items:**
- [ ] Search dialog.tra for Viconia lines
- [ ] Find VICONIA##.WAV files (or VVICONI##.WAV?)
- [ ] Select 5-10 samples (~20-30s total):
  - Sarcastic remarks
  - Drow superiority comments
  - Cold/aloof statements
  - Rare vulnerable moments
  - Combat taunts
- [ ] Update create_reference.py with Viconia files
- [ ] Generate viconia_ref_multi.wav
- [ ] Update voices.json

**Estimated Time**: 30-45 minutes

---

### 4. Edwin
**Character**: Male wizard, sardonic arrogant voice
**Current**: Using preset "male_sardonic"
**Goal**: Custom multi-reference from original voice files

**Action Items:**
- [ ] Search dialog.tra for Edwin lines
- [ ] Find EDWIN##.WAV files
- [ ] Select 5-10 samples (~20-30s total):
  - Arrogant boasting
  - Internal monologue asides
  - Dismissive insults
  - Magic-related statements
  - Scheming/plotting tones
- [ ] Update create_reference.py with Edwin files
- [ ] Generate edwin_ref_multi.wav
- [ ] Update voices.json

**Estimated Time**: 30-45 minutes

---

## Phase 2: Extended Companions

### 5. Aerie
**Character**: Female avariel elf, timid gentle voice
**Action Items:**
- [ ] Find AERIE##.WAV files
- [ ] Select samples: shy, nervous, kind, caring, distressed
- [ ] Create aerie_ref_multi.wav

### 6. Korgan
**Character**: Male dwarf, gruff aggressive voice
**Action Items:**
- [ ] Find KORGAN##.WAV files
- [ ] Select samples: bloodthirsty, rude, combat-eager, greedy
- [ ] Create korgan_ref_multi.wav

### 7. Anomen
**Character**: Male human, noble conflicted voice
**Action Items:**
- [ ] Find ANOMEN##.WAV files
- [ ] Select samples: righteous, doubtful, proud, humble moments
- [ ] Create anomen_ref_multi.wav

### 8. Keldorn
**Character**: Male paladin, older wise voice
**Action Items:**
- [ ] Find KELDORN##.WAV files
- [ ] Select samples: noble, wise, determined, compassionate
- [ ] Create keldorn_ref_multi.wav

### 9. Nalia
**Character**: Female noble, idealistic young voice
**Action Items:**
- [ ] Find NALIA##.WAV files
- [ ] Select samples: idealistic, caring, noble-born, magic-focused
- [ ] Create nalia_ref_multi.wav

### 10. Haer'Dalis
**Character**: Male tiefling bard, theatrical flowery voice
**Action Items:**
- [ ] Find HAERDALI##.WAV or similar
- [ ] Select samples: theatrical, poetic, romantic, dramatic
- [ ] Create haerdalis_ref_multi.wav

---

## Batch Workflow

### Step 1: Create All References (2-3 hours)
Execute for each character:
```powershell
cd "C:\Users\tenod\source\repos\BG2 Voiceover"

# 1. Find voice files
Get-ChildItem "BG2 Files\WAV Files" -Filter "MINSC*.WAV"

# 2. Listen and select samples
# (Use preview script or Windows Media Player)

# 3. Update create_reference.py
# Edit IMOEN_FILES section to CHARACTER_FILES

# 4. Run to create reference
python scripts/create_reference.py

# 5. Verify output
Get-Item "refs\minsc_ref_multi.wav"
```

**Deliverable**: Multi-reference files for all characters

### Step 2: Update Configuration (15 minutes)
Edit `data/voices.json`:
```json
{
  "_default_": "narrator",
  "Imoen": "C:\\...\\refs\\imoen_ref_multi.wav",
  "Minsc": "C:\\...\\refs\\minsc_ref_multi.wav",
  "Jaheira": "C:\\...\\refs\\jaheira_ref_multi.wav",
  "Viconia": "C:\\...\\refs\\viconia_ref_multi.wav",
  "Edwin": "C:\\...\\refs\\edwin_ref_multi.wav",
  "Aerie": "C:\\...\\refs\\aerie_ref_multi.wav",
  "Korgan": "C:\\...\\refs\\korgan_ref_multi.wav",
  "Anomen": "C:\\...\\refs\\anomen_ref_multi.wav",
  "Keldorn": "C:\\...\\refs\\keldorn_ref_multi.wav",
  "Nalia": "C:\\...\\refs\\nalia_ref_multi.wav",
  "HaerDalis": "C:\\...\\refs\\haerdalis_ref_multi.wav"
}
```

### Step 3: Prepare Lines (30-60 minutes)
Add all dialogue to `data/lines.csv`:
```csv
StrRef,Speaker,Text
38606,Imoen,Wow, a golem. I am sure that it is worth thousands upon thousands of gold pieces. Too bad we cannot fit it into our packs!
38607,Minsc,I do not like this place. It smells of magic and danger.
38608,Jaheira,Nature has no place here. We should not linger.
...
```

**Sources for lines:**
- Existing dialogue needing voice
- New mod content
- Player-added dialogue
- Restored cut content

### Step 4: Batch Synthesis (6-8 hours)
```powershell
cd "C:\Users\tenod\source\repos\BG2 Voiceover"

# Clear old builds if needed
# Remove-Item "build\OGG\*.wav" -Force

# Run batch synthesis (will take hours)
python scripts/synth.py
```

**Note**: 
- First line takes ~3 minutes (model loading)
- Subsequent lines ~30-60 seconds each
- Can run overnight
- Monitor for errors periodically

### Step 5: Quality Check (1-2 hours)
Listen to random samples from each character:
```powershell
# Play samples
Start-Process "build\OGG\38606.wav"  # Imoen
Start-Process "build\OGG\38607.wav"  # Minsc
Start-Process "build\OGG\38608.wav"  # Jaheira
# etc.
```

**Quality checklist:**
- [ ] Sounds like character
- [ ] Appropriate emotion
- [ ] Clear pronunciation
- [ ] No artifacts/clipping
- [ ] Correct audio format

### Step 6: Package Mod (30 minutes)
```powershell
# Deploy all to mod folder
Copy-Item "build\OGG\*.wav" "mod\vvoBG\OGG\" -Force

# Update TP2 to include all StrRefs
# (May need to expand from single line to multiple components)

# Copy to game
$GameDir = "E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition"
Copy-Item -Path "mod\vvoBG" -Destination $GameDir -Recurse -Force

# Install
cd $GameDir
.\setup-vvoBG.exe --uninstall 0
.\setup-vvoBG.exe --install 0
```

### Step 7: In-Game Testing (1-2 hours)
Test dialogue for each character:
- [ ] Imoen - golem line
- [ ] Minsc - battle cry
- [ ] Jaheira - nature comment
- [ ] Viconia - sarcastic remark
- [ ] Edwin - arrogant boast
- [ ] Others as available

---

## Tools to Create

### `scripts/batch_preview.py`
Preview all character voice files at once:
```python
# Show available files for each companion
# Calculate recommended sample combinations
# Estimate total reference duration
```

### `scripts/create_all_references.py`
Automate reference creation for all characters:
```python
# Loop through character definitions
# Create multi-reference for each
# Validate output format
# Update voices.json automatically
```

### `scripts/validate_synthesis.py`
Check quality of synthesized batch:
```python
# Verify all files exist
# Check audio format
# Detect clipping/silence
# Generate quality report
```

---

## Risk Management

### Potential Issues

**1. Filename Pattern Variations**
- **Risk**: Different characters may use different naming (e.g., OHIMOEN vs IMOEN)
- **Mitigation**: Verify with directory listing before assuming pattern
- **Tool**: `Get-ChildItem` with wildcards

**2. Insufficient Source Audio**
- **Risk**: Some characters may have fewer voice files
- **Mitigation**: Accept shorter references (15-20s) if needed
- **Fallback**: Use presets for minor characters

**3. Voice Quality Inconsistency**
- **Risk**: Some original files may be lower quality
- **Mitigation**: Choose clearest samples, skip noisy/overlapping audio
- **Validation**: Listen to reference before synthesizing

**4. Synthesis Failures**
- **Risk**: Index-TTS may fail on certain texts
- **Mitigation**: Sanitize text (remove tags, special chars)
- **Recovery**: Manual retry with simplified text

**5. Performance Issues**
- **Risk**: Batch synthesis may take 12+ hours
- **Mitigation**: Run overnight, use GPU if available
- **Alternative**: Process in smaller batches

---

## Success Criteria

### Phase 1 Complete When:
✅ 4 core companions have multi-references
✅ Test synthesis sounds character-accurate
✅ voices.json updated and working
✅ Quality matches Imoen standard

### Phase 2 Complete When:
✅ All companions have multi-references
✅ Large dialogue set synthesized
✅ Mod packaged and installable
✅ In-game testing validates quality

### Project Complete When:
✅ All companion dialogue synthesized
✅ Mod playable start-to-finish
✅ Voice quality consistent across characters
✅ Documentation complete for maintenance
✅ Workflow repeatable for future additions

---

## Timeline Estimate

### Optimistic (GPU, No Issues)
- Phase 1: 3-4 hours
- Phase 2: 6-8 hours
- Total: 10-12 hours

### Realistic (CPU, Minor Issues)
- Phase 1: 5-6 hours
- Phase 2: 10-12 hours
- Total: 15-18 hours

### Pessimistic (Issues, Troubleshooting)
- Phase 1: 8-10 hours
- Phase 2: 15-20 hours
- Total: 25-30 hours

**Recommended approach**: Phase 1 first, validate quality, then commit to Phase 2

---

## Next Immediate Actions

1. **Choose first target**: Minsc (distinct voice, should be easy to validate)
2. **Find voice files**: Search for MINSC*.WAV
3. **Select samples**: 5-10 with emotional variety
4. **Create reference**: Run create_reference.py
5. **Test synthesis**: Single line to validate quality
6. **If successful**: Proceed with remaining Phase 1 characters
7. **If issues**: Troubleshoot before scaling

---

**Ready to proceed with Phase 1, starting with Minsc?**
