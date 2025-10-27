# Near Infinity Bulk Export Guide

## Overview

Use Near Infinity to extract ALL companion dialogue lines in minutes instead of hours of manual work.

## Prerequisites

- **Near Infinity** installed (download from https://github.com/Argent77/NearInfinity)
- **BG2EE** installation at: `E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition`

## Step 1: Export String Table (dialog.tlk)

This gets ALL game text with StrRef numbers.

### In Near Infinity:

1. **Open game**: File → Open Game → Select BG2EE directory
2. **Navigate**: Resource Tree → TLK Files → `dialog.tlk`
3. **Export**: Click `dialog.tlk` → Menu: Edit → Export → CSV
4. **Save as**: `C:\Users\tenod\source\repos\BG2 Voiceover\exports\ni\dialog_tlk.csv`

**Expected output format:**
```csv
StrRef,Text,Flags,SoundRef,VolumeVariance,PitchVariance
0,"",0,"",0,0
1,"",0,"",0,0
...
38606,"Wow, a golem. I am sure that it is worth thousands upon thousands of gold pieces. Too bad we cannot fit it into our packs!",0,"",0,0
```

## Step 2: Export Companion DLG Files

This gets Speaker context (which character owns which lines).

### Priority Companions (Phase 1):

Export these DLG files in order:

1. **IMOEN.DLG** or **IMOENJ.DLG** (Throne of Bhaal)
2. **MINSC.DLG** or **MINSCJ.DLG**
3. **JAHEIRA.DLG** or **JAHEIRAJ.DLG**
4. **VICONIA.DLG** or **VVICONI.DLG**
5. **EDWIN.DLG** or **EDWINJ.DLG**

### In Near Infinity (for each):

1. **Navigate**: Resource Tree → DLG Files → `MINSC.DLG` (example)
2. **Export**: Click file → Menu: Edit → Export → CSV (Dialog Tree)
3. **Save as**: `exports\ni\MINSC_dlg.csv`

**Expected output format:**
```csv
State,Response,StrRef,Actor,NextDialog,Trigger,Action,Text
0,0,38607,MINSC,,-,-,"I do not like this place. It smells of magic and danger."
1,0,38608,MINSC,,-,-,"Boo says we should be careful here."
```

**Repeat for all companions.**

## Step 3: Join Data with Python

Now combine TLK + DLG exports to create `data/lines.csv`.

### Script: `scripts/near_infinity_join.py`

```python
"""
Join Near Infinity exports to create lines.csv
"""
import csv
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "exports" / "ni"
OUTPUT = ROOT / "data" / "lines.csv"

# Character DLG file mappings
COMPANIONS = {
    "IMOEN": "Imoen",
    "IMOENJ": "Imoen",
    "MINSC": "Minsc",
    "MINSCJ": "Minsc",
    "JAHEIRA": "Jaheira",
    "JAHEIRAJ": "Jaheira",
    "VICONIA": "Viconia",
    "VVICONI": "Viconia",
    "EDWIN": "Edwin",
    "EDWINJ": "Edwin",
    "AERIE": "Aerie",
    "AERIEJ": "Aerie",
    "KORGAN": "Korgan",
    "KORGANJ": "Korgan",
    "ANOMEN": "Anomen",
    "ANOMENJ": "Anomen",
    "KELDORN": "Keldorn",
    "KELDORJ": "Keldorn",
    "NALIA": "Nalia",
    "NALIAJ": "Nalia",
    "HAERDALI": "HaerDalis",
    "HAERDA": "HaerDalis",
}

def load_tlk(tlk_csv):
    """Load StrRef -> Text mapping from dialog.tlk export"""
    strref_map = {}
    
    with open(tlk_csv, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                strref = int(row['StrRef'])
                text = row['Text'].strip()
                if text:  # Only keep non-empty
                    strref_map[strref] = text
            except (ValueError, KeyError):
                continue
    
    return strref_map

def load_dlg_files(exports_dir):
    """Load all DLG exports and map StrRef -> Speaker"""
    strref_speakers = {}
    
    for dlg_file in exports_dir.glob("*_dlg.csv"):
        # Extract character name from filename (e.g., MINSC_dlg.csv -> MINSC)
        dlg_stem = dlg_file.stem.replace("_dlg", "").upper()
        
        # Map to canonical speaker name
        speaker = COMPANIONS.get(dlg_stem, dlg_stem.title())
        
        with open(dlg_file, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    strref = int(row.get('StrRef', -1))
                    if strref > 0:
                        # First speaker wins if multiple claim same StrRef
                        if strref not in strref_speakers:
                            strref_speakers[strref] = speaker
                except (ValueError, KeyError, TypeError):
                    continue
    
    return strref_speakers

def main():
    print("=" * 60)
    print("Near Infinity Bulk Join")
    print("=" * 60)
    
    # Load TLK
    tlk_file = EXPORTS / "dialog_tlk.csv"
    if not tlk_file.exists():
        print(f"❌ Error: {tlk_file} not found!")
        print("   Export dialog.tlk from Near Infinity first.")
        return
    
    print(f"\n📁 Loading TLK: {tlk_file}")
    strref_text = load_tlk(tlk_file)
    print(f"   ✓ Loaded {len(strref_text):,} text entries")
    
    # Load DLG files
    print(f"\n📁 Loading DLG exports from: {EXPORTS}")
    dlg_files = list(EXPORTS.glob("*_dlg.csv"))
    if not dlg_files:
        print("❌ Error: No *_dlg.csv files found!")
        print("   Export companion DLG files from Near Infinity first.")
        return
    
    print(f"   Found {len(dlg_files)} DLG files:")
    for f in dlg_files:
        print(f"     - {f.name}")
    
    strref_speakers = load_dlg_files(EXPORTS)
    print(f"   ✓ Mapped {len(strref_speakers):,} StrRefs to speakers")
    
    # Join and write output
    print(f"\n📝 Creating {OUTPUT}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    
    lines_written = 0
    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['StrRef', 'Speaker', 'Text'])
        
        for strref, speaker in sorted(strref_speakers.items()):
            text = strref_text.get(strref)
            if text:
                writer.writerow([strref, speaker, text])
                lines_written += 1
    
    print(f"   ✓ Wrote {lines_written:,} lines")
    
    # Summary by speaker
    speaker_counts = defaultdict(int)
    for speaker in strref_speakers.values():
        speaker_counts[speaker] += 1
    
    print(f"\n📊 Lines per speaker:")
    for speaker, count in sorted(speaker_counts.items(), key=lambda x: -x[1]):
        print(f"   {speaker:15s}: {count:4,} lines")
    
    print(f"\n✅ Done! Output: {OUTPUT}")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

### Run the script:

```powershell
cd "C:\Users\tenod\source\repos\BG2 Voiceover"
python scripts/near_infinity_join.py
```

## Step 4: Verify Output

Check `data/lines.csv`:

```powershell
# Count total lines
(Get-Content "data\lines.csv" | Measure-Object -Line).Lines

# Show first few lines
Get-Content "data\lines.csv" -TotalCount 10

# Count by speaker
Import-Csv "data\lines.csv" | Group-Object Speaker | Select-Object Name, Count | Sort-Object Count -Descending
```

## Expected Results

### Before (Manual):
- ⏱️ 30-60 minutes per character
- 🔢 Maybe 50-100 lines extracted
- 😰 Error-prone, tedious

### After (Near Infinity):
- ⏱️ 5-10 minutes total
- 🔢 Thousands of lines (500-2000 per companion)
- ✅ Complete, automated

## Troubleshooting

### "dialog.tlk export is huge"
- Normal! Full BG2EE has 100k+ strings
- Script filters to only lines with speakers

### "DLG export has no StrRef column"
- Make sure you select **"Export Dialog Tree"** not just "Export"
- Try "Export as CSV" with different options in Near Infinity

### "Character not found"
- Check filename pattern: should be `CHARACTER_dlg.csv`
- Add custom mapping to `COMPANIONS` dict in script

### "Multiple speakers claim same StrRef"
- Normal for shared lines (e.g., "Yes?")
- Script uses first speaker found (usually correct context)
- Can be de-duplicated later if needed

## Next Steps

After creating `data/lines.csv`:

1. ✅ You now have ALL companion dialogue
2. ✅ Ready for multi-reference synthesis
3. ✅ Can filter by speaker for batch processing
4. ✅ Can prioritize high-frequency lines

---

**Ready to export? Let's get thousands of lines in minutes!** 🚀
