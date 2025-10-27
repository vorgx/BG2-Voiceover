# Voice Audition System

## Overview

Test 2-3 voice variants for a character before committing to full synthesis. Prevents wasted time on poor voice choices.

## Why Audition?

**Without auditions:**
- Synthesize hundreds of lines with wrong voice
- Discover quality issues too late
- Waste hours regenerating everything

**With auditions:**
- Test 3 variants in 5 minutes
- Compare side-by-side with different emotions
- Make informed choice before bulk synthesis

## Quick Start

### Basic Usage

```powershell
cd "C:\Users\tenod\source\repos\BG2 Voiceover"
python scripts/audition.py Minsc
```

This will:
1. Load Minsc's character profile
2. Generate 3 voice variants (suggested presets)
3. Test each with 3 emotional phrases
4. Open comparison report in browser

### Custom Phrases

```powershell
python scripts/audition.py Jaheira neutral angry commanding
```

Test with specific emotional contexts.

## How It Works

### Step 1: Character Analysis

Audition system reads `data/characters.csv` to understand:
- **Gender** (M/F) - filters preset options
- **Archetype** (Boisterous, Stern, etc.) - suggests matching presets
- **Energy** (VeryHigh, Medium, Low) - validates energy match
- **Timbre** (Boomy, Cool, Wise) - ensures voice quality fits

### Step 2: Variant Selection

**Automatically generates 3 variants:**

1. **Current Preset** (if character has one)
2. **Suggested Presets** (based on archetype)
3. **Multi-Reference** (if reference file exists)

**Example for Minsc:**
- Variant 1: `male_booming` (current preset)
- Variant 2: `male_strong` (alternative)
- Variant 3: `male_heroic` (alternative)

### Step 3: Test Phrase Generation

Each variant is tested with multiple emotional contexts:

**Default phrases:**
- **Neutral**: "I understand. We should proceed with caution."
- **Happy**: "Excellent! This is exactly what we needed to find."
- **Angry**: "That's the last time I'll tolerate such behavior!"

**Additional options:**
- **Sad**: "I... I'm not sure I can go on like this anymore."
- **Commanding**: "Everyone, listen carefully. Here's what we're going to do."

### Step 4: Comparison Report

HTML report generated in `auditions/` folder with:
- ✅ Character profile summary
- ✅ Side-by-side audio players
- ✅ All emotional variants
- ✅ Quick selection buttons

## Preset Suggestions by Archetype

The system automatically suggests appropriate presets:

### Female Characters

| Archetype | Suggested Presets |
|-----------|-------------------|
| Cheery | female_bright, female_light, female_uplift |
| Stern | female_mature, female_strong, female_flat |
| Sardonic | female_cool, female_mature, female_sardonic |
| Timid | female_gentle, female_light, female_soft |
| Idealist | female_uplift, female_bright, female_gentle |

### Male Characters

| Archetype | Suggested Presets |
|-----------|-------------------|
| Boisterous | male_booming, male_strong, male_heroic |
| Arrogant | male_sardonic, male_cool, male_smooth |
| Stoic | male_flat, male_deep, male_wise |
| Charming | male_smooth, male_theatrical, male_noble |
| Menacing | male_deep, male_menacing, male_dark |
| Righteous | male_noble, male_wise, male_heroic |

## Complete Workflow

### Phase 1: Setup

1. Ensure character is in `data/characters.csv`
2. Set status to `Pending`

```powershell
python scripts/character_lib.py update Minsc Pending
```

### Phase 2: Audition

3. Run audition for character

```powershell
python scripts/audition.py Minsc
```

4. Browser opens with comparison report
5. Listen to all variants
6. Note which variant sounds best

### Phase 3: Selection

7. Update `data/characters.csv` with chosen preset:

```csv
Minsc,...,male_booming,...,Auditioned
```

8. Update `data/voices.json`:

```json
{
  "Minsc": {
    "voice": "male_booming"
  }
}
```

9. Update status:

```powershell
python scripts/character_lib.py update Minsc Auditioned
```

### Phase 4: Test Synthesis

10. Test with real dialogue:

```csv
# Add to data/lines.csv
99999,Minsc,"Go for the eyes, Boo! GO FOR THE EYES!"
```

11. Synthesize:

```powershell
python scripts/synth.py
```

12. Listen to `build/OGG/99999.wav`

### Phase 5: Lock

13. If quality is good:

```powershell
python scripts/character_lib.py update Minsc Locked
```

## Advanced Usage

### Audition with Multi-Reference

If you've already created a multi-reference file:

1. Update `characters.csv`:
```csv
Minsc,...,male_booming,refs/minsc_ref_multi.wav,Pending
```

2. Run audition:
```powershell
python scripts/audition.py Minsc
```

Now includes 4th variant using your reference!

### Compare Preset + Reference

Test both approaches:

```csv
# Character with both preset and reference
Jaheira,...,female_mature,refs/jaheira_ref_multi.wav,Pending
```

Audition generates:
- Variant 1: `female_mature` preset only
- Variant 2: Other suggested preset
- Variant 3: Multi-reference clone

### Custom Emotional Mix

For specific character personalities:

```powershell
# Minsc (heroic, simple)
python scripts/audition.py Minsc neutral happy commanding

# Edwin (arrogant, scheming)
python scripts/audition.py Edwin neutral angry sad

# Aerie (timid, compassionate)
python scripts/audition.py Aerie neutral sad happy
```

## Output Files

### Audio Files

```
auditions/
  ├── Minsc_1_neutral.wav      # Variant 1, neutral phrase
  ├── Minsc_1_happy.wav         # Variant 1, happy phrase
  ├── Minsc_1_angry.wav         # Variant 1, angry phrase
  ├── Minsc_2_neutral.wav      # Variant 2, neutral phrase
  ├── Minsc_2_happy.wav
  ├── Minsc_2_angry.wav
  ├── Minsc_3_neutral.wav      # Variant 3, neutral phrase
  └── ...
```

### Report File

```
auditions/
  └── Minsc_audition.html      # Comparison report
```

**Note**: `auditions/` folder is gitignored (temporary files)

## Troubleshooting

### "Character not found"

Check spelling in `data/characters.csv`:
```powershell
python scripts/character_lib.py status
```

### "Failed to generate audio"

Index-TTS may have model loading issues:
- Wait 2-3 minutes for models to load
- Check Index-TTS is properly installed
- Verify config.yaml paths are correct

### "No variants generated"

Character needs preset suggestions:
1. Check `characters.csv` has `Archetype` filled
2. Manually add `VoicePreset` field
3. Or create multi-reference first

### "Audio sounds wrong"

This is expected! That's why we audition:
- Try different preset combinations
- Adjust emotional phrase mix
- Consider creating custom multi-reference

## Best Practices

### DO:
✅ Audition before bulk synthesis
✅ Test multiple emotional contexts
✅ Compare preset vs reference (if both available)
✅ Get second opinion (play for someone else)
✅ Update characters.csv immediately after choosing

### DON'T:
❌ Skip auditions for important characters
❌ Test with only one emotional phrase
❌ Rush the decision
❌ Forget to update voices.json
❌ Leave character in "Pending" after audition

## Example: Complete Audition Session

### Minsc (Boisterous Ranger)

**Command:**
```powershell
python scripts/audition.py Minsc neutral happy commanding
```

**Variants Generated:**
1. Current: `male_booming` ⭐ (Winner!)
2. Suggested: `male_strong` (too generic)
3. Suggested: `male_heroic` (too serious)

**Decision:** `male_booming` matches Minsc's personality perfectly

**Actions:**
```powershell
# Update status
python scripts/character_lib.py update Minsc Auditioned

# voices.json already correct, test synthesis
python scripts/synth.py

# Quality confirmed, lock it
python scripts/character_lib.py update Minsc Locked
```

### Jaheira (Stern Druid)

**Command:**
```powershell
python scripts/audition.py Jaheira neutral angry sad
```

**Variants Generated:**
1. Current: `female_mature` (too soft)
2. Suggested: `female_strong` (too aggressive)
3. Multi-ref: `refs/jaheira_ref_multi.wav` ⭐ (Winner!)

**Decision:** Multi-reference captures her authoritative-but-caring tone

**Actions:**
```csv
# Update characters.csv
Jaheira,...,female_mature,refs/jaheira_ref_multi.wav,Auditioned
```

```json
// Update voices.json
{
  "Jaheira": {
    "voice": "female_mature",
    "ref": "refs/jaheira_ref_multi.wav",
    "emo_alpha": 0.9
  }
}
```

```powershell
python scripts/character_lib.py update Jaheira Locked
```

## Integration with Workflow

### Position in Pipeline

```
1. Character defined (Draft)
2. Status → Pending
3. 🎤 AUDITION ← You are here
4. Update voices.json
5. Status → Auditioned
6. Test synthesis
7. Status → Locked
8. Bulk synthesis
```

### Time Investment

- **Audition**: 5-10 minutes per character
- **Bulk synthesis without audition**: 1-2 hours (wasted if wrong voice)
- **ROI**: 10 minutes saves hours of rework

---

**Version:** 1.0  
**Updated:** October 26, 2025  
**Status:** Production-ready audition system
