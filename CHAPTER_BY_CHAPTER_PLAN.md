# Chapter-by-Chapter Voice Synthesis Plan

## Strategic Approach: Chapter 1 First

**Why this works:**
- ✅ Manageable scope (test the full pipeline)
- ✅ Early feedback (validate quality before scaling)
- ✅ Iterative refinement (improve process between chapters)
- ✅ Playable milestones (can test in-game immediately)

---

## Phase 1: Chapter Definition & Analysis

### Step 1.1: Identify Chapter 1 Scope

**What is "Chapter 1" in BG2EE?**

Suggested definition:
- **Start**: Character creation → Irenicus dungeon
- **End**: Escape to Athkatla surface
- **Key locations**: Dungeon levels 1-3, Yoshimo encounter, exit to city
- **Duration**: First ~2-3 hours of gameplay

**Alternative definitions:**
- **Narrow**: Just the dungeon (easier, faster)
- **Broad**: Dungeon + Copper Coronet + first quest (more content)

**Recommendation**: Start with dungeon only, expand if successful.

### Step 1.2: Identify All NPCs in Chapter 1

**Method: Use Near Infinity**

1. **Load BG2EE in Near Infinity**
2. **Navigate to Areas**:
   - `AR0602.ARE` - Irenicus Dungeon Level 1
   - `AR0603.ARE` - Irenicus Dungeon Level 2
   - `AR0604.ARE` - Irenicus Dungeon Level 3
   - etc.

3. **For each area, list all creatures**:
   - Click area → "View/Edit" tab
   - Expand "Actors" section
   - Note creature resource (e.g., `MEPHIT01.CRE`)

4. **For each creature, check for dialog**:
   - Open `.CRE` file
   - Look for "Dialog" field
   - If not empty (e.g., `YOSHIMO.DLG`), this NPC speaks

**Alternative: Grep search**

```powershell
# Find all dialog references in area files
Select-String -Path "BG2 Files\*.ARE" -Pattern "\.DLG" | Select-Object -Unique
```

### Step 1.3: Categorize NPCs by Voice Priority

**Priority Levels:**

#### **Priority 1: Story-Critical NPCs** (MUST HAVE)
- Have multiple lines
- Required for progression
- Player interacts frequently

*Example: Yoshimo, Irenicus (if appears), named enemies*

#### **Priority 2: Interactive NPCs** (SHOULD HAVE)
- Optional but common interactions
- Quest-related
- Memorable encounters

*Example: Trapped prisoners, merchants, minor quest givers*

#### **Priority 3: Ambient NPCs** (NICE TO HAVE)
- One-line interactions
- Flavor text
- Generic responses

*Example: Generic guards, random prisoners, background characters*

#### **Priority 4: Generic Creatures** (OPTIONAL)
- Combat barks only
- Non-speaking (just sound effects)
- Already have voice sets

*Example: Mephits, golems, generic monsters*

**Action**: Create spreadsheet of all Chapter 1 NPCs with priority

---

## Phase 2: NPC Voice Design System

### Step 2.1: Voice Decision Framework

**For each NPC, determine voice characteristics:**

#### **Inputs** (from game data):

1. **Race** (from `.CRE` file → "Race" field)
   - Human, Elf, Dwarf, Halfling, Gnome
   - Half-elf, Half-orc, Tiefling
   - Monster races

2. **Gender** (from `.CRE` file → "Gender" field)
   - Male, Female

3. **Class** (from `.CRE` file → "Class" field)
   - Fighter, Mage, Thief, Cleric, etc.

4. **Alignment** (from `.CRE` file → "Alignment" field)
   - Lawful Good, Chaotic Evil, etc.

5. **Name** (from `.CRE` file → "Long name" or "Script name")

6. **Context** (from lore/wiki/dialogue)
   - Story role (ally, enemy, neutral)
   - Personality traits
   - Background

#### **Decision Tree**:

```
IF Priority 1-2 (important NPCs):
  └─> Design custom voice profile
      └─> Check for existing BG1/BG2 audio
          ├─> YES: Extract & create multi-reference
          └─> NO: Design preset-based voice
              └─> Use Race + Gender + Class + Alignment formula

IF Priority 3-4 (minor NPCs):
  └─> Use generic preset based on Race + Gender only
```

### Step 2.2: Race-Based Voice Profiles

**Default voice mappings by race:**

```csv
Race,Gender,Archetype,Energy,Timbre,DefaultPreset
Human,M,Neutral,Medium,Neutral,male_flat
Human,F,Neutral,Medium,Neutral,female_mature
Elf,M,Noble,Low,Smooth,male_smooth
Elf,F,Gentle,Low,Light,female_gentle
Dwarf,M,Gruff,High,Gruff,male_gruff
Dwarf,F,Strong,Medium,Strong,female_strong
Halfling,M,Cheerful,High,Light,male_light
Halfling,F,Cheerful,High,Bright,female_bright
Gnome,M,Eccentric,High,Nasal,male_eccentric
Gnome,F,Bright,High,Bright,female_bright
Half-Orc,M,Aggressive,High,Deep,male_deep
Half-Orc,F,Strong,High,Strong,female_strong
Drow,M,Sardonic,Medium,Cool,male_cool
Drow,F,Sardonic,Medium,Cool,female_cool
Tiefling,M,Theatrical,Medium,Smooth,male_theatrical
Tiefling,F,Mysterious,Medium,Smooth,female_smooth
```

**Modifiers by class:**

```csv
Class,EnergyModifier,TimbreModifier,ArchetypeHint
Fighter,+1 Energy,Stronger,Commanding
Mage,+0 Energy,Wise,Intellectual
Thief,-1 Energy,Quieter,Sneaky
Cleric,+0 Energy,Calm,Righteous
Ranger,-1 Energy,Rough,Stoic
Bard,+1 Energy,Melodic,Charming
```

**Modifiers by alignment:**

```csv
Alignment,ArchetypeHint,EmoAlpha
Lawful Good,Righteous,1.0
Neutral Good,Kind,1.0
Chaotic Good,Rebellious,1.1
Lawful Neutral,Formal,0.8
True Neutral,Detached,0.7
Chaotic Neutral,Unpredictable,1.2
Lawful Evil,Menacing,0.9
Neutral Evil,Cruel,1.0
Chaotic Evil,Maniacal,1.3
```

### Step 2.3: Automated Voice Assignment Tool

**Create**: `scripts/npc_voice_designer.py`

```python
"""
Automatically suggest voice profiles for NPCs based on game data.
"""

def analyze_creature(cre_file):
    """
    Read .CRE file and extract:
    - Name, Race, Gender, Class, Alignment
    - Dialog file reference
    """
    # Parse .CRE with Near Infinity export or binary reader
    pass

def suggest_voice(race, gender, class_type, alignment, name, priority):
    """
    Apply decision tree to recommend voice preset or reference.
    
    Returns:
    {
        "preset": "male_gruff",
        "archetype": "Gruff Fighter",
        "energy": "High",
        "timbre": "Gruff",
        "emo_alpha": 1.0,
        "confidence": "High"  # Based on data completeness
    }
    """
    pass

def create_character_entry(npc_data):
    """
    Generate CSV row for characters.csv
    """
    pass
```

**This tool will**:
1. Read all `.CRE` files in Chapter 1 areas
2. Auto-suggest voice for each
3. Generate `data/chapter1_characters.csv`
4. Flag high-priority NPCs for manual review

### Step 2.4: Can Index-TTS Handle This?

**Yes, BUT with caveats:**

#### **What Index-TTS CAN do:**
✅ Clone voices from reference audio (multi-ref approach works!)
✅ Use presets for generic character types
✅ Adjust emotion via `emo_alpha`, `emo_text`
✅ Handle varied dialogue (neutral, angry, happy, etc.)
✅ Process thousands of lines (batch mode)

#### **What Index-TTS CANNOT do:**
❌ Create dramatically different voices on-demand (limited preset variety)
❌ Perfect character-specific quirks (e.g., Minsc's exact hamster enthusiasm)
❌ Non-human voices (monsters, creatures) - sounds too human
❌ Extreme pitch/timbre shifts (dwarf depth, gnome nasality limited)

#### **When you need something else:**

**For non-human creatures (Priority 4):**
- Use **ElevenLabs** (better creature/monster voices)
- Use **Bark** or **Tortoise TTS** (more variety)
- Use **existing BG voice sets** (combat barks, creature sounds)
- Skip VO entirely (rely on text + generic sounds)

**For very specific character voices:**
- Find **professional voice actors** on Fiverr/Upwork
- Use **commercial voice cloning** (ElevenLabs, Resemble.ai)
- Extract from **other RPG games** (legal grey area)

**Recommendation**: 
- Use **Index-TTS for 90%** (humanoid NPCs)
- Use **existing game sounds for 10%** (monsters, creatures)

---

## Phase 3: Bulk Extraction for Chapter 1

### Step 3.1: Export Chapter 1 Dialog

**Near Infinity bulk export:**

1. **Identify all DLG files for Chapter 1 NPCs**
   ```
   YOSHIMO.DLG
   DLGJAILX.DLG
   DLGDUNGE.DLG
   etc.
   ```

2. **Export each as CSV** (Dialog Tree format)

3. **Save to**: `exports/ni/chapter1/`

### Step 3.2: Filter by StrRef Range (Optional)

BG2 dialog is roughly organized by chapter. If you know StrRef ranges:

```powershell
# Extract only StrRefs between X and Y
$chapter1Range = 1000..5000  # Example range
Import-Csv "exports\ni\dialog_tlk.csv" | 
    Where-Object {$_.StrRef -in $chapter1Range} |
    Export-Csv "exports\ni\chapter1_dialog.csv"
```

### Step 3.3: Run Bulk Join

```powershell
python scripts/near_infinity_join.py --chapter 1
```

**Modify script** to accept chapter filter:
- Input: List of DLG files for Chapter 1
- Output: `data/chapter1_lines.csv`

### Step 3.4: Validate Coverage

```powershell
# Count lines by speaker
Import-Csv "data\chapter1_lines.csv" | 
    Group-Object Speaker | 
    Sort-Object Count -Descending |
    Select-Object Name, Count

# Check for missing NPCs
# Compare against NPC list from Phase 2
```

---

## Phase 4: Automation Pipeline for Chapter 1

### Step 4.1: Automated Voice Assignment

**Input**: `data/chapter1_characters.csv` (from Phase 2)

**Process**:
1. For Priority 1-2 NPCs with existing audio:
   - Auto-detect voice files (e.g., YOSHIMO##.WAV)
   - Run `create_reference.py` automatically
   - Generate multi-reference for each

2. For Priority 1-2 NPCs without audio:
   - Use NPC voice designer suggestions
   - Run audition mode for top 5-10
   - Lock voices after approval

3. For Priority 3-4 NPCs:
   - Use race/gender defaults
   - No auditions (too many)
   - Batch assign presets

**Script**: `scripts/auto_assign_voices.py`

```python
"""
Automatically assign voices to all Chapter 1 NPCs.
"""

def assign_chapter_voices(chapter_characters_csv, output_voices_json):
    """
    Read chapter1_characters.csv
    Apply voice design rules
    Generate voices.json entries
    Flag NPCs needing manual review
    """
    
    for npc in read_csv(chapter_characters_csv):
        if npc.priority <= 2 and has_existing_audio(npc):
            # Create multi-reference
            create_multi_ref(npc)
        elif npc.priority <= 2:
            # Flag for audition
            flag_for_audition(npc)
        else:
            # Auto-assign preset
            assign_default_preset(npc)
    
    write_voices_json(output_voices_json)
```

### Step 4.2: Batch Reference Creation

For NPCs with existing audio:

```powershell
# Process all Priority 1-2 NPCs
python scripts/batch_create_references.py --chapter 1 --priority 1-2
```

**Script**:
- Reads `chapter1_characters.csv`
- Finds audio files for each NPC
- Creates multi-reference automatically
- Updates `refs/` folder

### Step 4.3: Batch Auditions

For NPCs without audio:

```powershell
# Run auditions for top NPCs
python scripts/batch_audition.py --chapter 1 --priority 1-2 --auto-suggest
```

**Output**:
- `auditions/chapter1/`
- One HTML report per NPC
- Review queue list

**Manual step**: Listen and approve voices

### Step 4.4: Batch Synthesis

Once all voices locked:

```powershell
# Synthesize all Chapter 1 lines
python scripts/synth.py --input data/chapter1_lines.csv --chapter 1
```

**Features**:
- Progress bar (e.g., "542/1247 lines complete")
- Parallel processing (if possible)
- Resume from interruption
- QA sampling (auto-flag outliers)

**Estimated time**: 
- 1000 lines × 30 seconds = 8-10 hours
- Run overnight

### Step 4.5: Quality Assurance

**Automated checks**:

```python
# scripts/qa_check.py
for audio_file in chapter1_audio:
    - Check duration (too short < 0.5s or too long > 30s)
    - Check volume (too quiet or clipping)
    - Check format (must be mono 22050Hz)
    - Flag anomalies
```

**Manual sampling**:
- Listen to 2% random sample (20 out of 1000)
- Check Priority 1 NPCs fully
- Validate emotion match (angry lines sound angry)

### Step 4.6: Deployment

**Package Chapter 1 mod**:

```powershell
# Create chapter-specific TP2
python scripts/package_chapter.py --chapter 1

# Test install
cd "E:\...\Baldur's Gate II Enhanced Edition"
.\setup-vvoBG_chapter1.exe --install 0
```

**In-game validation**:
- Play through Chapter 1
- Verify all voiced NPCs work
- Check for missing audio
- Validate StrRef mapping

---

## Phase 5: Iteration & Refinement

### Step 5.1: Gather Feedback

**Metrics to track**:
- Voice quality (1-10 scale)
- Emotion appropriateness
- Character match
- Technical issues (cut-off, distortion)

### Step 5.2: Identify Issues

**Common problems**:
- Wrong emotion for context
- Voice too generic (all NPCs sound same)
- Technical glitches (clipping, wrong format)
- Missing lines (StrRef not mapped)

### Step 5.3: Refine Process

Before Chapter 2:
- Update voice assignment rules
- Improve automation scripts
- Add better QA checks
- Document lessons learned

---

## Chapter 1 Implementation Timeline

### Week 1: Preparation
- **Day 1-2**: Define Chapter 1 scope, list all NPCs
- **Day 3-4**: Create NPC voice designer tool
- **Day 5-7**: Bulk extract dialog, validate coverage

### Week 2: Voice Design
- **Day 8-10**: Auto-assign voices for all NPCs
- **Day 11-12**: Create multi-references for Priority 1-2
- **Day 13-14**: Run auditions, lock voices

### Week 3: Synthesis
- **Day 15-17**: Batch synthesize (overnight runs)
- **Day 18-19**: QA checks, fix issues
- **Day 20-21**: Final validation

### Week 4: Deployment & Testing
- **Day 22-23**: Package mod, test install
- **Day 24-26**: In-game playthrough
- **Day 27-28**: Gather feedback, refine

**Total**: ~4 weeks for Chapter 1 (1000-2000 lines)

---

## Scaling to Subsequent Chapters

**Chapter 2** (Athkatla City):
- Apply lessons from Chapter 1
- Reuse companion voices (already locked)
- Focus on new NPCs only
- Faster: ~2-3 weeks

**Chapter 3+**:
- Established workflow
- Most common NPCs already voiced
- Only new characters need design
- Fastest: ~1-2 weeks each

---

## Tools Summary

### New Tools to Create:

1. **`scripts/npc_voice_designer.py`**
   - Auto-suggest voices from .CRE data
   - Generate chapter-specific characters.csv

2. **`scripts/auto_assign_voices.py`**
   - Batch assign voices to NPCs
   - Flag for audition vs auto-preset

3. **`scripts/batch_create_references.py`**
   - Auto-create multi-refs for NPCs with audio
   - Process entire chapter at once

4. **`scripts/batch_audition.py`**
   - Run auditions for multiple NPCs
   - Generate review queue

5. **`scripts/qa_check.py`**
   - Automated quality checks
   - Flag anomalies for review

6. **`scripts/package_chapter.py`**
   - Create chapter-specific WeiDU mod
   - Handle StrRef ranges

### Existing Tools (Already Have):

- ✅ `scripts/synth.py` (synthesis engine)
- ✅ `scripts/create_reference.py` (multi-ref builder)
- ✅ `scripts/audition.py` (voice testing)
- ✅ `scripts/character_lib.py` (tracking)
- ✅ `scripts/near_infinity_join.py` (bulk extract)

---

## Decision Points

### Do we need this before starting?

**Essential:**
- ✅ Chapter 1 scope definition
- ✅ NPC voice designer tool
- ✅ Bulk extraction working
- ✅ Basic automation for batch synthesis

**Nice to have:**
- ⏳ Perfect voice assignment rules (iterate)
- ⏳ Full automation (manual steps OK for Ch1)
- ⏳ Advanced QA (basic checks sufficient)

### Can we start immediately?

**Yes, with current tools + 2-3 days of prep:**

1. **Day 1**: Define Chapter 1 NPCs manually
2. **Day 2**: Create simple NPC voice designer
3. **Day 3**: Test workflow on 5-10 NPCs

Then scale from proven approach.

---

## Your Next Steps

### Option A: Manual Chapter 1 (Fastest Start)
1. List 20-30 Chapter 1 NPCs manually
2. Assign voices using character library
3. Use existing tools to synthesize
4. Learn what automation is needed

### Option B: Build Automation First (Better Long-term)
1. Create NPC voice designer tool
2. Create batch automation scripts
3. Test on Chapter 1 subset
4. Run full Chapter 1 pipeline

**Recommendation**: **Option A** for Chapter 1, build automation as you identify pain points, then use automation for Chapter 2+.

---

**What do you think? Should we:**
1. Start with manual Chapter 1 to learn the process?
2. Build the NPC voice designer tool first?
3. Something else?
