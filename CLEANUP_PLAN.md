# Repository Cleanup Plan

## 📊 Current State Analysis

### Structure Overview:
```
BG2 Voiceover/
├── Root Level (25 items) - 🔴 CLUTTERED
├── scripts/ (17 files) - 🟡 MODERATE
├── docs/ (13 files) - 🟡 NEEDS CONSOLIDATION
├── data/ (12 files) - 🟢 MOSTLY GOOD
├── config/ (2 files) - 🟢 GOOD
├── src/bg2vo/ (5 files) - 🟢 GOOD
├── tests/ (2 files) - 🟢 GOOD
├── Empty directories (3) - 🔴 DELETE
```

---

## 🎯 Cleanup Objectives

1. **Reduce root-level clutter** (too many loose MD files)
2. **Consolidate documentation** (13 docs → organized structure)
3. **Remove empty/unused directories**
4. **Archive obsolete planning documents**
5. **Organize scripts by purpose**
6. **Clean up test/temporary files**

---

## 📋 Detailed Cleanup Plan

### PHASE 1: Archive Obsolete Planning Documents
**Impact**: Low risk - these are historical/planning docs

**Actions**:
```
CREATE: archive/ directory

MOVE TO archive/:
  ✓ CHAPTER_BY_CHAPTER_PLAN.md        # Historical planning doc
  ✓ SCALING_PLAN.md                   # Future roadmap (superseded by current work)
  ✓ VOICE_IMPROVEMENT_LOG.md          # Historical log
  ✓ LESSONS_LEARNED.md                # Historical notes
  ✓ agent.md (root duplicate)         # Duplicate of docs/AGENT.md
```

**Rationale**: These docs have historical value but clutter the root. Keep in archive for reference.

---

### PHASE 2: Consolidate Documentation
**Impact**: Medium risk - reorganize docs

**Actions**:
```
RESTRUCTURE docs/ into subdirectories:

docs/
├── getting-started/
│   ├── README.md (new - entry point)
│   ├── INTEGRATION_STATUS.md (current status/testing)
│   └── CHAPTER_PIPELINE.md (workflow guide)
│
├── guides/
│   ├── NEAR_INFINITY_EXPORT_STEPS.md
│   ├── VOICES_JSON_GUIDE.md
│   ├── CHARACTERS_CSV_GUIDE.md
│   ├── AUDITION_GUIDE.md
│   └── TEST_DEPLOYMENT.md
│
├── reference/
│   ├── ARCHITECTURE.md
│   ├── PRESETS.md
│   ├── USAGE.md
│   └── TESTING.md
│
└── dev/
    ├── AGENT.md
    └── NEAR_INFINITY_GUIDE.md (merge with EXPORT_STEPS?)

CONSOLIDATE/MERGE:
  ✓ NEAR_INFINITY_GUIDE.md + NEAR_INFINITY_EXPORT_STEPS.md
    → guides/NEAR_INFINITY.md (single comprehensive guide)
```

---

### PHASE 3: Remove Empty/Unused Directories
**Impact**: Low risk - no data loss

**Actions**:
```
DELETE:
  ✓ tools/ (empty, unused)
  ✓ auditions/ (empty, will be created when needed)
  ✓ .github/workflows/ (empty, no CI/CD yet)
```

**Rationale**: Empty directories create confusion. Can recreate when needed.

---

### PHASE 4: Organize Scripts by Purpose
**Impact**: Low risk - but requires import path updates

**Actions**:
```
RESTRUCTURE scripts/ into subdirectories:

scripts/
├── core/                      # Essential workflow scripts
│   ├── convert_d_to_csv.py
│   ├── near_infinity_join.py
│   ├── synth.py
│   └── deploy.py
│
├── voice_design/              # Voice reference/audition tools
│   ├── audition.py
│   ├── create_reference.py
│   ├── build_cards.py
│   └── build_refs.py
│
├── utils/                     # Helper scripts
│   ├── check_progress.py
│   ├── verify_install.py
│   ├── test_audio.py
│   └── preview_imoen_audio.py
│
└── stubs/                     # Blueprint stubs (not yet implemented)
    ├── gen_pseudorefs.py
    ├── synth_cache.py
    └── character_lib.py (unused?)

CONSIDER DELETING:
  ? convert_dialog_txt.py (redundant with convert_d_to_csv.py?)
  ? character_lib.py (stub, not referenced anywhere)
```

**Note**: Reorganizing scripts requires updating any hardcoded paths.

---

### PHASE 5: Clean Data Directory
**Impact**: Medium risk - preserve actual data

**Actions**:
```
KEEP AS-IS:
  ✓ chapter1_lines.csv          # Active dataset
  ✓ chapter1_split/             # Active dataset
  ✓ chapter1_targets.csv        # Active metadata
  ✓ voices.json                 # Active config
  ✓ lines.csv                   # Master dataset
  ✓ characters.csv              # Character voice library (active reference)

MOVE TO archive/data/:
  ✓ dlg_chapter_map.csv         # Reference data (not actively used)
  ✓ dlg_summary.csv             # Analysis output (can regenerate)
  ✓ speaker_summary.csv         # Analysis output (can regenerate)
  ✓ gap_report_*.csv            # Analysis outputs (can regenerate)

DELETE:
  ✓ test_lines.csv              # Temporary test file (can recreate)
```

**Rationale**: Keep active workflow files in data/, archive reference/analysis files.

---

### PHASE 6: Update Root README
**Impact**: Low risk - documentation only

**Actions**:
```
UPDATE README.md to reflect:
  ✓ New directory structure
  ✓ Quick start guide
  ✓ Link to docs/getting-started/README.md
  ✓ Remove obsolete workflow sections
  ✓ Add link to INTEGRATION_STATUS.md for testing
```

---

## 📁 Proposed Final Structure

```
BG2 Voiceover/
├── README.md                    # Updated with new structure
├── .gitignore
├── README-WeiDU.html           # WeiDU reference (keep)
│
├── archive/                    # NEW - historical docs
│   ├── CHAPTER_BY_CHAPTER_PLAN.md
│   ├── SCALING_PLAN.md
│   ├── VOICE_IMPROVEMENT_LOG.md
│   ├── LESSONS_LEARNED.md
│   └── data/                   # Archived data files
│       ├── characters.csv
│       ├── dlg_chapter_map.csv
│       └── ...
│
├── config/                     # Configuration templates
│   ├── defaults.yaml
│   └── voices.sample.json
│
├── data/                       # Active datasets only
│   ├── lines.csv
│   ├── voices.json
│   ├── chapter1_lines.csv
│   ├── chapter1_targets.csv
│   └── chapter1_split/
│
├── docs/                       # Organized documentation
│   ├── getting-started/
│   ├── guides/
│   ├── reference/
│   └── dev/
│
├── scripts/                    # Organized by purpose
│   ├── core/
│   ├── voice_design/
│   ├── utils/
│   └── stubs/
│
├── src/bg2vo/                  # Python package (no change)
│   ├── __init__.py
│   ├── config.py
│   ├── lines.py
│   ├── voices.py
│   └── audit.py
│
├── tests/                      # Test suite (no change)
│   ├── conftest.py
│   └── test_bg2vo_core.py
│
├── build/                      # Build outputs (keep as-is)
├── mod/                        # WeiDU mod (keep as-is)
├── refs/                       # Voice references (keep as-is)
├── exports/                    # Near Infinity exports (keep as-is)
└── BG2 Files/                  # Game assets (keep as-is)
```

---

## ⚠️ Risk Assessment

### LOW RISK (Safe to proceed):
- Archive planning docs ✅
- Delete empty directories ✅
- Move analysis CSVs to archive ✅
- Update README ✅

### MEDIUM RISK (Verify first):
- Reorganize docs/ structure
  - **Check**: No hardcoded doc paths in scripts
- Move data files to archive
  - **Check**: No scripts reference archived CSVs

### HIGH RISK (Requires testing):
- Reorganize scripts/ structure
  - **Impact**: May break import paths
  - **Mitigation**: Update imports, test all scripts after
  - **Alternative**: Leave scripts/ flat for now

---

## 🎯 Recommended Phased Approach

### Phase A: Safe Cleanup (DO FIRST)
1. Create `archive/` directory
2. Move planning docs to archive
3. Delete empty directories (tools/, auditions/, .github/workflows/)
4. Delete test_lines.csv
5. Commit: "chore: archive planning docs and clean empty dirs"

### Phase B: Data Cleanup (DO SECOND)
1. Create `archive/data/` directory
2. Move analysis CSVs to archive
3. Verify no scripts reference them
4. Commit: "chore: archive analysis data files"

### Phase C: Documentation Restructure (DO THIRD)
1. Create docs subdirectories
2. Move docs to new structure
3. Update any doc cross-references
4. Update root README
5. Commit: "docs: reorganize into structured directories"

### Phase D: Scripts Reorganization (OPTIONAL - LATER)
1. Create scripts subdirectories
2. Move scripts (keep imports working)
3. Update any import statements
4. Test all scripts
5. Commit: "refactor: organize scripts by purpose"

---

## 📝 Post-Cleanup Checklist

After each phase:
- [ ] Run tests: `pytest tests/`
- [ ] Verify key scripts work:
  - [ ] `python scripts/synth.py --help`
  - [ ] `python scripts/check_progress.py --chapter 1`
  - [ ] `python scripts/deploy.py --help`
- [ ] Check documentation links
- [ ] Git status clean (no unintended changes)
- [ ] Create git commit with clear message

---

## 💡 Additional Recommendations

### After Cleanup:
1. **Add .gitignore entries**:
   ```
   build/OGG/*.wav
   __pycache__/
   .pytest_cache/
   *.pyc
   ```

2. **Create CONTRIBUTING.md**:
   - Document directory structure
   - Explain where to add new files
   - Testing requirements

3. **Add scripts/README.md**:
   - Explain script organization
   - Quick reference for what each script does

---

## ⏱️ Estimated Time

- Phase A (Safe Cleanup): 10 minutes
- Phase B (Data Cleanup): 15 minutes
- Phase C (Doc Restructure): 30 minutes
- Phase D (Scripts Reorganize): 45 minutes

**Total**: ~1.5 - 2 hours for complete cleanup

---

## 🚦 Decision Required

**What to proceed with?**

Options:
1. **Conservative**: Phase A + B only (safest, minimal disruption)
2. **Moderate**: Phase A + B + C (clean + organized docs)
3. **Aggressive**: All phases (complete reorganization)

**Recommendation**: Start with **Phase A + B** (safe cleanup), then reassess before documentation restructure.
