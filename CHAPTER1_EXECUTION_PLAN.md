# Chapter 1 Execution Plan - Option B (Phased with Testing Gates)

**Last Updated**: October 26, 2025  
**Total Lines**: 905 (Jaheira: 516, Minsc: 257, Imoen: 65, Others: 67)  
**Current Progress**: 2/905 lines (0.2% - Imoen test only)

---

## Overview

Phased approach with **approval gates** at each step:
1. Create voice reference from original BG2 audio (~30 sec)
2. Test reference with 5-10 lines
3. Review quality and **get user approval** before proceeding
4. Move to next character
5. Test batch of 50 lines (mixed speakers)
6. Full overnight synthesis only after all approvals

---

## Phase 1: Create & Test Jaheira Voice Reference

### 1.1 Extract Original Audio Samples

**Available Files**: `BG2 Files/WAV Files/JAHEIR*.WAV` (JAHEIR01-10+)

**Goal**: Create ~30 second reference with diverse emotional range

**Steps**:
```powershell
# Check Jaheira files
Get-ChildItem "BG2 Files\WAV Files\JAHEIR*.WAV" | ForEach-Object {
    Write-Host $_.Name
    # Listen to each, note which have good quality and variety
}
```

**Selection Criteria**:
- Clear speech (no background noise)
- Varied emotional tones (neutral, concerned, angry, happy)
- Good audio quality
- Different sentence structures (short, long, question, statement)

**Target**: Select 5-8 clips that total ~30 seconds

### 1.2 Create Reference File

```powershell
# Use create_reference.py to combine selected samples
python scripts/voice_design/create_reference.py \
  --speaker Jaheira \
  --samples "BG2 Files/WAV Files/JAHEIR01.WAV" "BG2 Files/WAV Files/JAHEIR05.WAV" "BG2 Files/WAV Files/JAHEIR08.WAV" \
  --output refs/jaheira_ref.wav \
  --target-duration 30
```

**Output**: `refs/jaheira_ref.wav` (~30 seconds)

### 1.3 Update voices.json

```powershell
# Update Jaheira entry in data/voices.json
```

**Before**:
```json
"Jaheira": {
  "voice": "refs/imoen_ref.wav",
  "preset": "female_mature",
  "notes": "Mature female, wise guardian, stern but caring",
  "status": "Pending"
}
```

**After**:
```json
"Jaheira": {
  "voice": "refs/jaheira_ref.wav",
  "preset": "female_mature",
  "notes": "Mature female, wise guardian, stern but caring",
  "status": "Testing"
}
```

### 1.4 Test with 5-10 Lines

**Create test file**: `data/test_jaheira.csv`

```powershell
# Extract first 10 Jaheira lines
python -c "
import csv
with open('data/chapter1_lines.csv', 'r', encoding='utf-8') as src, \
     open('data/test_jaheira.csv', 'w', newline='', encoding='utf-8') as dst:
    reader = csv.DictReader(src)
    writer = csv.DictWriter(dst, fieldnames=reader.fieldnames)
    writer.writeheader()
    count = 0
    for row in reader:
        if row['Speaker'] == 'Jaheira' and count < 10:
            writer.writerow(row)
            count += 1
"
```

**Synthesize test**:
```powershell
python scripts/core/synth.py --input data/test_jaheira.csv
```

**Expected**: 10 WAV files in `build/OGG/`, ~5-10 minutes

### 1.5 Review & Approval Gate 🚦

**User Review**:
1. Listen to all 10 generated Jaheira lines
2. Check voice quality:
   - ✅ Sounds like Jaheira?
   - ✅ Appropriate tone/emotion?
   - ✅ Clear pronunciation?
   - ✅ Consistent quality across all 10?
3. **Decision**: Approve or Iterate

**If APPROVED**: Mark status "Locked" in voices.json, proceed to Phase 2  
**If NOT APPROVED**: Adjust reference (try different samples), retest

---

## Phase 2: Create & Test Minsc Voice Reference

### 2.1 Extract Original Audio Samples

**Available Files**: `BG2 Files/WAV Files/MINSC*.WAV` (MINSC01-10+)

**Goal**: Create ~30 second reference with Minsc's booming personality

**Steps**:
```powershell
# Check Minsc files
Get-ChildItem "BG2 Files\WAV Files\MINSC*.WAV" | ForEach-Object {
    Write-Host $_.Name
    # Listen to each, select clips with varied emotions
}
```

**Selection Criteria**:
- Minsc's characteristic booming voice
- Battle cries, calm moments, humor
- Boo references (if available)
- Clear and energetic delivery

**Target**: Select 5-8 clips that total ~30 seconds

### 2.2 Create Reference File

```powershell
python scripts/voice_design/create_reference.py \
  --speaker Minsc \
  --samples "BG2 Files/WAV Files/MINSC01.WAV" "BG2 Files/WAV Files/MINSC03.WAV" "BG2 Files/WAV Files/MINSC07.WAV" \
  --output refs/minsc_ref.wav \
  --target-duration 30
```

**Output**: `refs/minsc_ref.wav` (~30 seconds)

### 2.3 Update voices.json

**Before**:
```json
"Minsc": {
  "voice": "refs/imoen_ref.wav",
  "preset": "male_booming",
  "notes": "Male heroic, booming voice, brave warrior",
  "status": "Pending"
}
```

**After**:
```json
"Minsc": {
  "voice": "refs/minsc_ref.wav",
  "preset": "male_booming",
  "notes": "Male heroic, booming voice, brave warrior",
  "status": "Testing"
}
```

### 2.4 Test with 5-10 Lines

**Create test file**: `data/test_minsc.csv`

```powershell
# Extract first 10 Minsc lines
python -c "
import csv
with open('data/chapter1_lines.csv', 'r', encoding='utf-8') as src, \
     open('data/test_minsc.csv', 'w', newline='', encoding='utf-8') as dst:
    reader = csv.DictReader(src)
    writer = csv.DictWriter(dst, fieldnames=reader.fieldnames)
    writer.writeheader()
    count = 0
    for row in reader:
        if row['Speaker'] == 'Minsc' and count < 10:
            writer.writerow(row)
            count += 1
"
```

**Synthesize test**:
```powershell
python scripts/core/synth.py --input data/test_minsc.csv
```

**Expected**: 10 WAV files in `build/OGG/`, ~5-10 minutes

### 2.5 Review & Approval Gate 🚦

**User Review**:
1. Listen to all 10 generated Minsc lines
2. Check voice quality:
   - ✅ Sounds like Minsc?
   - ✅ Booming/heroic tone?
   - ✅ Clear pronunciation?
   - ✅ Matches character personality?
3. **Decision**: Approve or Iterate

**If APPROVED**: Mark status "Locked" in voices.json, proceed to Phase 3  
**If NOT APPROVED**: Adjust reference (try different samples), retest

---

## Phase 3: Verify Imoen Reference (Only 2 Lines Done)

### 3.1 Current Status

**Existing Reference**: `refs/imoen_ref_multi.wav` ✅  
**Lines Generated**: Only 2 test lines (38537, 38606)  
**Total Needed**: 65 lines

**Goal**: Validate reference quality before generating remaining 63 lines

### 3.2 Check Reference Duration

```powershell
# Check if Imoen ref is ~30 seconds
# If not, may need to recreate with more samples
```

### 3.3 Test with 10 More Lines

**Create test file**: `data/test_imoen.csv`

```powershell
# Extract 10 Imoen lines (different from the 2 already done)
python -c "
import csv
with open('data/chapter1_lines.csv', 'r', encoding='utf-8') as src, \
     open('data/test_imoen.csv', 'w', newline='', encoding='utf-8') as dst:
    reader = csv.DictReader(src)
    writer = csv.DictWriter(dst, fieldnames=reader.fieldnames)
    writer.writeheader()
    count = 0
    done_strrefs = {'38537', '38606'}  # Already generated
    for row in reader:
        if row['Speaker'] == 'Imoen' and row['StrRef'] not in done_strrefs and count < 10:
            writer.writerow(row)
            count += 1
"
```

**Synthesize test**:
```powershell
python scripts/core/synth.py --input data/test_imoen.csv
```

**Expected**: 10 WAV files in `build/OGG/`, ~5-10 minutes

### 3.4 Review & Approval Gate 🚦

**User Review**:
1. Listen to all 10 new Imoen lines (plus the 2 existing)
2. Check consistency across 12 total samples
3. Check voice quality:
   - ✅ Consistent with previous 2 lines?
   - ✅ Appropriate youthful tone?
   - ✅ Clear pronunciation?
   - ✅ Sounds like Imoen?
4. **Decision**: Approve or Recreate Reference

**If APPROVED**: Mark status "Locked" in voices.json, proceed to Phase 4  
**If NOT APPROVED**: Recreate reference with better samples (~30 sec), retest

---

## Phase 4: Test Synthesis - 50 Lines Mixed Speakers

**Goal**: Validate all three approved voices work well together in a batch

### 4.1 Create Test Batch

**Create**: `data/test_50_lines.csv` with mix:
- 25 Jaheira lines (top priority)
- 15 Minsc lines  
- 10 Imoen lines (new ones, not already done)

```powershell
python -c "
import csv
with open('data/chapter1_lines.csv', 'r', encoding='utf-8') as src, \
     open('data/test_50_lines.csv', 'w', newline='', encoding='utf-8') as dst:
    reader = csv.DictReader(src)
    writer = csv.DictWriter(dst, fieldnames=reader.fieldnames)
    writer.writeheader()
    
    counts = {'Jaheira': 0, 'Minsc': 0, 'Imoen': 0}
    targets = {'Jaheira': 25, 'Minsc': 15, 'Imoen': 10}
    done_strrefs = {'38537', '38606'}  # Already done
    
    for row in reader:
        speaker = row['Speaker']
        if speaker in counts and counts[speaker] < targets[speaker]:
            if speaker != 'Imoen' or row['StrRef'] not in done_strrefs:
                writer.writerow(row)
                counts[speaker] += 1
        
        if all(counts[s] >= targets[s] for s in targets):
            break
"
```

### 4.2 Synthesize Batch

```powershell
# This will take 25-50 minutes
python scripts/core/synth.py --input data/test_50_lines.csv

# Monitor progress (in another terminal)
python scripts/utils/check_progress.py --input data/test_50_lines.csv
```

**Expected**: 50 WAV files, ~30-50 minutes total

### 4.3 Review & Final Approval Gate 🚦

**User Review**:
1. Listen to random samples from each speaker (5-10 each)
2. Check:
   - ✅ All three voices distinct from each other?
   - ✅ Quality consistent across batch?
   - ✅ No technical issues (clipping, distortion, etc.)?
   - ✅ Happy with all three character voices?
3. **Decision**: Approve for Full Synthesis or Iterate

**If APPROVED**: Proceed to Phase 5 (full overnight batch)  
**If NOT APPROVED**: Identify issues, adjust references, retest

---

## Phase 5: Full Chapter 1 Synthesis (Approved Voices Only)

**Prerequisites**: ✅ All three references approved and locked

### 5.1 Pre-Flight Check

```powershell
# Verify voices.json status
# Ensure Jaheira, Minsc, Imoen all marked "Locked"

# Verify chapter1_lines.csv ready (905 lines)

# Check disk space (need ~500MB for 905 WAV files)
```

### 5.2 Start Overnight Synthesis

```powershell
# Run in dedicated terminal (will take 8-15 hours)
python scripts/core/synth.py --chapter 1
```

**Expected**:
- 905 WAV files total
- Skips already-generated test files (saves time)
- Duration: ~8-15 hours (30-60 sec per line)
- Best to run overnight

### 5.3 Monitor Progress

```powershell
# In separate terminal, check periodically:
python scripts/utils/check_progress.py --chapter 1

# Expected output:
# Completed: 234/905 (25.9%)
# Remaining: 671 lines
# Estimated: ~6 hours remaining
```

### 5.4 Verify Completion

**Next morning**:
```powershell
# Check final count
(Get-ChildItem "build\OGG\*.wav").Count
# Should be: 905

# Check for errors
python scripts/utils/check_progress.py --chapter 1
# Should show: 905/905 (100%)
```

---

## Phase 6: Deploy & In-Game Testing

### 6.1 Deploy to Mod Structure

```powershell
# Deploy all Chapter 1 files with OH prefix
python scripts/core/deploy.py --chapter 1 --generate-tp2

# Verify deployment
(Get-ChildItem "mod\vvoBG\OGG\OH*.wav").Count
# Should be: 905
```

### 6.2 Copy to Game Directory

```powershell
$GameDir = "E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition"

Copy-Item "mod\setup-vvoBG.exe" "$GameDir\"
Copy-Item "mod\vvoBG.tp2" "$GameDir\"
Copy-Item "mod\vvoBG" "$GameDir\" -Recurse -Force
```

### 6.3 Install WeiDU Mod

```powershell
cd "E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition"
.\setup-vvoBG.exe
# Type: I (Install)
```

### 6.4 Test In-Game

1. Launch BG2EE
2. Load save or start new game in Chapter 1 (Irenicus's Dungeon)
3. Test dialogue with:
   - Jaheira (major companion - should sound mature/wise)
   - Minsc (major companion - should sound booming/heroic)
   - Imoen (should sound youthful)
4. Verify audio plays for all StrRefs
5. Check volume levels are consistent

---

## Approval Checklist

- [ ] **Phase 1**: Jaheira reference approved (10 test lines sound good)
- [ ] **Phase 2**: Minsc reference approved (10 test lines sound good)
- [ ] **Phase 3**: Imoen reference verified (10 more test lines sound good)
- [ ] **Phase 4**: 50-line batch approved (all three voices work well together)
- [ ] **Phase 5**: Full 905 lines synthesized overnight
- [ ] **Phase 6**: Deployed and tested in-game successfully

---

## Rollback Plan

**If issues found at any phase:**

1. **Stop current synthesis** (if running)
2. **Identify problem**:
   - Voice doesn't match character?
   - Audio quality poor?
   - Technical issues (clipping, distortion)?
3. **Fix reference**:
   - Try different original audio samples
   - Adjust reference duration
   - Test different Index-TTS settings
4. **Retest with 10 lines** before proceeding
5. **Delete bad WAV files** before regenerating:
   ```powershell
   Remove-Item "build\OGG\<problematic_strrefs>.wav"
   ```

---

## Time Estimates

| Phase | Description | Duration |
|-------|-------------|----------|
| 1 | Jaheira ref creation + test | 1-2 hours |
| 2 | Minsc ref creation + test | 1-2 hours |
| 3 | Imoen verification | 30 min |
| 4 | 50-line batch test | 30-50 min |
| 5 | Full 905 lines (overnight) | 8-15 hours |
| 6 | Deploy + test | 1 hour |
| **Total** | **End-to-end** | **~2 days** |

**Today**: Phases 1-4 (4-6 hours active work)  
**Tonight**: Phase 5 (overnight, unattended)  
**Tomorrow**: Phase 6 (1 hour testing)

---

## Current Status

- [x] Repository cleaned and organized
- [x] AGENT.md updated with workflows
- [x] Original BG2 audio files located (Jaheira, Minsc available)
- [ ] **START HERE**: Phase 1 - Create Jaheira reference

**Ready to begin Phase 1?** Let me know and I'll help extract the Jaheira audio samples!
