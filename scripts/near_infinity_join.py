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
