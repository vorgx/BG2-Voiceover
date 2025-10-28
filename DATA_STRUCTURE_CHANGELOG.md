# Data Structure Changelog

This document tracks changes to the core data structures (CSVs, JSONs) to help identify issues if something breaks after updates.

## 2025-10-28: Column Rename and Addition

### Changed: all_lines.csv Structure

**Previous columns:**
```
StrRef, Speaker, Text, WAV_Reference, Chapter, DLG_File
```

**New columns:**
```
StrRef, Speaker, Text, Original_VO_WAV, Generated_VO_WAV, Chapter, DLG_File
```

**Changes:**
1. **Renamed:** `WAV_Reference` → `Original_VO_WAV`
   - **Reason:** Clarify that this is the original game audio filename (e.g., JAHEIR01)
   - **Content:** Same as before - references files in `BG2 Files/WAV Files/`
   - **Empty when:** Line has no original voiceover

2. **Added:** `Generated_VO_WAV` (new column)
   - **Purpose:** Track which lines have been synthesized by Index-TTS
   - **Content:** Filename of generated audio in `build/OGG/` (e.g., "1001.wav")
   - **Empty when:** Line not yet synthesized
   - **Future:** Will be auto-populated by synth_batch.py after synthesis

### Scripts Updated

**Must use new column names:**
- ✅ `scripts/utils/extract_emotion_refs.py` - Changed to `Original_VO_WAV`
- ✅ `scripts/utils/validate_data.py` - Changed to `Original_VO_WAV`
- ✅ `scripts/utils/build_complete_lines_db.py` - Changed to `Original_VO_WAV`, `DLG_File`, added `Generated_VO_WAV`
- ✅ `scripts/utils/split_chapters.py` - Changed to `Original_VO_WAV`, `DLG_File`
- ✅ `scripts/utils/filter_chapter1_for_synth.py` - Changed to `Original_VO_WAV`
- ✅ `scripts/utils/filter_unvoiced_lines.py` - Changed to `Original_VO_WAV`
- ✅ `scripts/utils/populate_generated_vo.py` - Populates `Generated_VO_WAV` column
- ✅ `scripts/utils/cleanup_duplicate_audio.py` - Archives duplicates, clears `Generated_VO_WAV`
- ✅ `scripts/core/synth_batch.py` - Now checks `Original_VO_WAV` and skips those lines

**No changes needed:**
- ✅ `scripts/utils/update_project_stats.py` - Works with StrRef matching only

### Migration Notes

**Completed migration on 2025-10-28:**
1. ✅ Restored original CSV from git commit f56b44f
2. ✅ Created `migrate_all_lines_structure.py` for proper 6→7 column migration
3. ✅ Successfully migrated 49,328 rows with correct structure
4. ✅ Populated `Generated_VO_WAV` column with 1,566 synthesized files
5. ✅ Archived 19 duplicate audio files (lines with both original and synthesized)
6. ✅ Updated all scripts and documentation for new column names

**If scripts fail with KeyError:**
- Check if script references `WAV_Reference` or `Source_File`
- Update to use `Original_VO_WAV` or `DLG_File` instead
- Check this changelog for list of updated scripts

### Duplicate Audio Prevention

**New behavior (implemented 2025-10-28):**
- `synth_batch.py` now checks `Original_VO_WAV` column before synthesis
- Lines with original professional voice acting are automatically skipped
- Prevents unnecessary over-synthesis of already-voiced lines
- `cleanup_duplicate_audio.py` safely archives any existing duplicates

### Automation Status

**Completed (2025-10-28):**
- ✅ `populate_generated_vo.py` - Scans build/OGG/ and updates `Generated_VO_WAV` column
- ✅ `synth_batch.py` - Skips lines with `Original_VO_WAV` (prevents duplicates)
- ✅ `cleanup_duplicate_audio.py` - Archives duplicate synthesized files

**Result:** System now tracks both original and synthesized audio, never overwrites professional voice acting

---

## Previous Changes

### 2025-10-XX: Column Rename Source_File → DLG_File
- Renamed last column for clarity
- No functional changes

### 2025-10-XX: Added Statistics Columns to characters.csv
- Added: `Total_Lines`, `VO_Lines`, `No_VO_Yet`
- Auto-populated by `update_project_stats.py`
