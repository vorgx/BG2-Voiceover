# Vocalization Enhancement Plan

## Overview
Improve detection and synthesis of non-verbal vocalizations (grunts, yells, screams, etc.) using pattern-based classification and Index-TTS emotion controls.

## Problem Statement
Lines like Jaheira's "Gllgghh!" (StrRef 20555) are currently synthesized literally, resulting in unnatural robotic speech. These should be detected as vocalizations and synthesized with emotion-driven audio prompts for authentic delivery.

## Solution Architecture

### Phase 1: Core Implementation (Steps 1-4)
**Goal:** Implement detection, classification, and enhanced synthesis with testing infrastructure.

#### Step 1: Pattern-Based Vocalization Detection
- **File:** `scripts/utils/classify_vocalizations.py`
- **Purpose:** Detect and classify vocalizations using regex patterns
- **Features:**
  - VocalizationType enum (GRUNT, SCREAM, MOAN, YELL, GASP, LAUGH, CRY, COUGH, SIGH, GENERIC)
  - Pattern matching with confidence scoring
  - Multi-word text support (classify each word separately)
  - Returns classification with confidence level

#### Step 2: Emotion Reference Library
- **File:** `scripts/utils/extract_emotion_refs.py`
- **Purpose:** Build curated emotion reference audio library
- **Features:**
  - Manual curation workflow (prompt user to classify existing audio)
  - Extract emotional clips from original game WAV files
  - Organize by character and emotion type
  - Generate emotion_refs.json mapping

#### Step 3: Enhanced Voice Configuration
- **File:** `data/voices.json` (structure update)
- **Purpose:** Add per-character emotion presets
- **Features:**
  - `emotion_presets` section per character
  - Map VocalizationType to emotion settings
  - Include emo_audio_prompt paths, emo_alpha values
  - Generic fallback presets for unmapped characters

#### Step 4: Enhanced Batch Synthesis
- **File:** `scripts/core/synth_batch.py` (enhancement)
- **Purpose:** Integrate vocalization detection and emotion synthesis
- **Features:**
  - Import classify_vocalizations module
  - Add `synthesize_vocalization()` function
  - Add `transform_vocalization_text()` for phonetic conversion
  - Route vocalizations to emotion-driven synthesis
  - Fall back to normal synthesis if not classified as vocalization

### Phase 2: Testing & Iteration (Steps 5-7)
**Goal:** Validate detection accuracy and synthesis quality.

#### Step 5: Test Suite
- **File:** `scripts/tests/test_vocalizations.py`
- **Purpose:** Validate detection and classification
- **Test Cases:**
  - Pattern matching accuracy
  - Confidence scoring
  - Edge cases (mixed text, punctuation)
  - Known examples (Jaheira's "Gllgghh!", other vocalizations)

#### Step 6: Pipeline Integration
- **File:** `scripts/core/split_chapters.py` (enhancement)
- **Purpose:** Add vocalization metadata to CSV output
- **Features:**
  - Add `VocalizationType` column
  - Add `VocalizationConfidence` column
  - Run classification during chapter splitting
  - Enable filtering/analysis of vocalization distribution

#### Step 7: Quality Iteration
- **Process:** Test synthesis with curated examples
- **Validation:**
  - Listen to generated vocalizations
  - Adjust emotion mappings (emo_alpha, emo_text)
  - Refine text transformations
  - Update pattern detection if needed
  - Document character-specific quirks

## Implementation Order

### Phase 1 (This Session)
1. ✅ Document plan (this file)
2. ✅ Commit current state
3. ⏳ Implement Step 1: `classify_vocalizations.py`
4. ⏳ Implement Step 2: `extract_emotion_refs.py`
5. ⏳ Implement Step 3: Enhanced `voices.json` structure
6. ⏳ Implement Step 4: Enhanced `synth_batch.py`
7. ⏳ Test with Jaheira's "Gllgghh!" and similar examples

### Phase 2 (Next Session)
8. Implement Step 5: `test_vocalizations.py`
9. Implement Step 6: Enhanced `split_chapters.py`
10. Implement Step 7: Quality iteration workflow

## Expected Outcomes

### Immediate Benefits
- Automatic detection of 95%+ of vocalizations
- Emotion-driven synthesis for natural delivery
- Character-specific emotion presets
- Extensible pattern library

### Long-term Benefits
- Improved overall voice quality perception
- Reduced manual post-processing
- Scalable to all chapters
- Framework for other special text handling (whispers, shouts, etc.)

## Test Examples

### Known Vocalizations from Chapter 1
- **Jaheira (20555):** "Gllgghh!" → GRUNT/YELL (pained, frustrated)
- **Jaheira (20558):** "No! Blast you filthy bogslimes! Not again!" → YELL (angry)
- **Jaheira (42213):** "Damn... damn you..." → CRY (grief)
- **Jaheira (26496):** "Heh..." → LAUGH (nervous/awkward)
- **Minsc:** Various "RAAAGH!" battle cries → YELL (battle fury)

### Edge Cases to Handle
- Mixed text: "I... *cough* *cough*... I am not here to grovel!"
- Trailing punctuation: "Gllgghh!!!!!!"
- Multiple vocalizations in one line: "*gasp* No... *sob*"
- Action descriptions: "*sigh*" vs "sigh" (word)

## Configuration Format

### voices.json Enhancement
```json
{
  "Jaheira": {
    "voice_id": "jaheira_v1",
    "emotion_presets": {
      "GRUNT": {
        "emo_audio_prompt": "refs/emotions/jaheira/pained_grunt.wav",
        "emo_text": "pained frustrated grunt",
        "emo_alpha": 0.8
      },
      "YELL": {
        "emo_audio_prompt": "refs/emotions/jaheira/angry_yell.wav",
        "emo_text": "angry determined yell",
        "emo_alpha": 0.7
      },
      "CRY": {
        "emo_audio_prompt": "refs/emotions/jaheira/grief_cry.wav",
        "emo_text": "grief stricken sobbing",
        "emo_alpha": 0.9
      }
    }
  }
}
```

## Success Metrics
- **Detection Accuracy:** >95% precision/recall on known vocalizations
- **Synthesis Quality:** Subjective improvement in naturalness (A/B testing)
- **Coverage:** All Chapter 1 vocalizations properly classified
- **Performance:** <500ms overhead per line for classification

## Rollback Plan
- All changes are additive (new files, enhanced existing)
- Vocalization synthesis is optional (falls back to normal synthesis)
- Can disable by removing emotion_presets from voices.json
- Git commit before implementation allows easy revert

---

**Status:** Planning Complete - Ready for Implementation
**Next Action:** Commit current state, then implement Steps 1-4
**Estimated Time:** 2-3 hours for Phase 1 implementation
