# Chapter Pipeline Checklist

A step-by-step guide for building a chapter’s voice dataset from raw game assets through sanitized line CSVs and synthesis-ready audio.

---

## 0. Prerequisites

- **Near Infinity** configured (see `../guides/NEAR_INFINITY_EXPORT_STEPS.md`).
- `BG2 Voiceover` repo cloned with Python 3.11+ (or your working environment) and scripts under `scripts/` available.
- Game assets exported or accessible via the configured BG2EE installation.

---

## 1. Export Source Data (Near Infinity)

1. Launch Near Infinity and open the BG2EE game directory.
2. Export `.D` dialogue files for the target scope (character-specific or mass export). Save into `BG2 Files/Dialog Files/` within the repo.
3. Optional: export `dialog.tlk` to `exports/ni/dialog_tlk.csv`. (The pipeline can read the binary TLK if missing.)

Reference: `../guides/NEAR_INFINITY_EXPORT_STEPS.md` for detailed export instructions and best practices.

---

## 2. Convert `.D` Files to StrRef CSVs

Run the converter script to generate `_dlg.csv` files (SAY-only StrRefs):

```powershell
py scripts\convert_d_to_csv.py
```

- Reads `.D` files from `BG2 Files/Dialog Files/`.
- Writes StrRef lists to `exports/ni/*_dlg.csv`.
- Confirms number of files converted and StrRefs extracted.

---

## 3. Join StrRefs with TLK Text

Build the master `data/lines.csv` by aligning StrRefs with actual dialogue text:

```powershell
py scripts\near_infinity_join.py
```

- Loads StrRefs from `exports/ni`.
- Reads `dialog.tlk` (binary or CSV fallback) to pull the full text.
- Outputs `data/lines.csv` containing `StrRef`, `Speaker`, and `Text`.

Tip: Inspect the script’s summary counts to verify expected coverage.

---

## 4. Sanitize Dialogue Text

Remove WeiDU placeholders and clean punctuation for TTS input using the sanitizer embedded in `scripts/synth.py`.

### Option A: batch sanitize CSVs

Use the helper snippet (adjust to target files) to rewrite sanitized text in place:

```python
import csv
from pathlib import Path
from scripts.synth import sanitize

def sanitize_file(path: Path) -> None:
    with path.open(newline='', encoding='utf-8') as src:
        reader = csv.DictReader(src)
        rows = list(reader)

    for row in rows:
        row['Text'] = sanitize(row['Text'])

    with path.open('w', newline='', encoding='utf-8') as dst:
        writer = csv.DictWriter(dst, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)

sanitize_file(Path('data/lines.csv'))
```

This ensures downstream tools see sanitized text (no `<CHARNAME>` tokens, no double spaces).

---

## 5. Extract Chapter Slice

Generate the chapter-specific lines CSV (e.g., Chapter 1) using existing mapping logic.

- If a script exists (e.g., `scripts/chapter_extract.py`), run it to create `data/chapterX_lines.csv` and `data/chapterX_split/*`.
- Otherwise, filter `data/lines.csv` by Chapter using available metadata (e.g., via pandas or manual StrRef lists).

Ensure the chapter CSV contains only the sanitized text column, not tokens.

---

## 6. Count Lines per Speaker

Before synthesis, tally line counts to plan voice workloads:

```python
import csv
from collections import Counter

counts = Counter()
with open('data/chapter1_lines.csv', newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        counts[row['Speaker']] += 1

print('Total lines:', sum(counts.values()))
for speaker, count in counts.most_common():
    print(speaker, count)
```

Use the results to schedule recording sessions or batch TTS runs (e.g., Chapter 1 totals: Jaheira 516, Minsc 257, Imoen 65…).

---

## 7. Configure Voices

Update or review `data/voices.json` to ensure each speaker has an assigned voice profile.

- See `../guides/VOICES_JSON_GUIDE.md` for schema details (CLI vs. advanced API parameters).
- Sanity-check that each Chapter speaker has a mapping; fallback `_default_` will be used otherwise.

---

## 8. Run Synthesis (Optional Stage Here)

With sanitized text and voice assignments in place, trigger TTS generation.

- The CLI version (per `scripts/synth.py`) expects appropriately configured IndexTTS paths.
- Because `synth.py` now wraps execution in `synth_all()`, run module only when ready:

  ```powershell
  py scripts\synth.py
  ```

- Audio files appear under `build/OGG/` named by StrRef.
- Consider chunking by speaker or Chapter for parallelism.

**⚠️ CRITICAL: Index-TTS is SLOW - Do not interrupt!**
- Each line takes 30-120 seconds to generate
- Terminal will appear frozen - this is normal
- Run overnight for large batches (900+ lines = 8-15 hours)
- Script automatically skips existing WAV files if interrupted

Tip: Always test a small subset before launching the full batch.

---

## 9. QA & Next Steps

- Spot-check sanitized text (`grep` for remaining `<TOKEN>` patterns) to catch missed placeholders.
- Validate audio output (listen to samples, ensure no missing files).
- Document any manual scripts or decisions in `docs/` for future chapters.

### Suggested QA Snippets

```python
import csv
from scripts.synth import sanitize

with open('data/chapter1_lines.csv', newline='', encoding='utf-8') as f:
    for i, row in enumerate(csv.DictReader(f)):
        cleaned = sanitize(row['Text'])
        assert '<' not in cleaned, (i, row['StrRef'])
```

---

## 10. Version Control & Handoff

- Commit regenerated CSVs and any new docs to keep the pipeline reproducible.
- Record counts and sanitization checks in a log (optional) for future reference.
- Update `CHAPTER_PIPELINE.md` if new steps or scripts are added during later chapters.

---

**Outcome:** Following this checklist takes you from raw `.D` exports to per-chapter sanitized line CSVs ready for voice assignment and synthesis—repeat for each chapter with minimal guesswork.
