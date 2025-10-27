# Near Infinity Export Guide - Step by Step

This guide shows you **exactly** how to export data from Near Infinity to CSV format.

## Prerequisites

- Near Infinity installed at: `C:\Users\tenod\AppData\Local\NearInfinity\NearInfinity.exe`
- BG2EE game at: `E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition`
- Create export directory in workspace: `C:\Users\tenod\source\repos\BG2 Voiceover\exports\`

---

## Part 1: Export dialog.tlk (String References) *(Optional)*

**Purpose:** Get all the text strings in the game (this contains all dialogue, item descriptions, etc.)

### Steps:

1. **Launch Near Infinity**
   - Double-click: `C:\Users\tenod\AppData\Local\NearInfinity\NearInfinity.exe`

2. **Open Your Game**
   - File → Open Game
   - Navigate to: `E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition`
   - Click "Select Folder"
   - Wait for game to load (may take 30-60 seconds)

3. **Find dialog.tlk**
   - In the left tree panel, expand "TLK Files"
   - Click on "dialog.tlk" (or "dialogF.tlk" for female voices)

4. **Export to CSV/TSV** *(if available)*
   - With `dialog.tlk` highlighted, go to Tools → Convert → TLK → Tab-separated (TSV) …
   - When prompted, choose **Save as:** `C:\Users\tenod\source\repos\BG2 Voiceover\exports\ni\dialog_tlk.csv`
   - (TSV is fine—just keep the `.csv` extension so our scripts pick it up.)
   - Wait for export to complete (progress shows in the status bar)

> 💡 **Can't see the TLK→TSV option?** No problem. Just skip this step. The `scripts/near_infinity_join.py` tool now reads the game’s binary `dialog.tlk` directly (either from `BG2 Files/dialog.tlk`, the Steam install, or a path you set in `BG2_DIALOG_TLK`).

**Expected Result:** You should get a CSV file with columns like:
```
StrRef,Text,SoundResRef,VolumeVariance,PitchVariance
0,"",,,
1,"",,,
2,"<CHARNAME>",,,
...
38606,"I am autonomous, by order of the Master.",OGOLEM02,,
```

---

## Part 2: Export DLG Files (Dialogue Trees)

**Purpose:** Get the dialogue structure - which StrRef belongs to which character, plus branching choices.

### Option A: Export Individual DLG Files (For Specific Characters)

1. **Still in Near Infinity** (from Part 1)

2. **Find a Character's DLG**
   - In the left tree panel, expand "DLG - Dialogues"
   - Scroll to find the character (e.g., "IMOEN.DLG", "MINSC.DLG")
   - Click on it to open

3. **Export to CSV/TSV**
   - Tools → Convert → DLG → Tab-separated (TSV)…
   - **Save as:** `C:\Users\tenod\source\repos\BG2 Voiceover\exports\IMOEN_dlg.csv`
   - Confirm the export (status bar will blink when done)

4. **Repeat** for each character you want

### Option B: Export ALL DLG Files (Bulk Export)

**Warning:** This exports 1000+ files and may take 10-20 minutes.

1. **Still in Near Infinity**

2. **Select DLG Section**
   - In the left tree panel, right-click on "DLG - Dialogues" (the folder itself)

3. **Batch Export**
   - Choose Tools → Mass Export… (Ctrl+M)
   - In the left column, select **DLG**
   - Set **Output directory** to: `C:\Users\tenod\source\repos\BG2 Voiceover\BG2 Files\Dialog Files\`
   - Make sure **Decompile scripts and dialogs** is checked; uncheck everything else
   - Click **Export** and wait (large batch can take 10–20 minutes)

> 📝 This version of Near Infinity writes `.d` text files during mass export. That’s exactly what we want—`scripts/convert_d_to_csv.py` turns them into `_dlg.csv` files automatically.

**Expected Result:** You’ll end up with hundreds of `.D` files (e.g. `IMOEN2.D`, `MINSC.D`, …) in `BG2 Files/Dialog Files/`.

---

## Part 3: Export Area Creature Lists (NPC Inventory)

**Purpose:** Find out which NPCs exist in which areas (for chapter-by-chapter planning).

### Steps:

1. **Still in Near Infinity**

2. **Find Chapter 1 Areas**
   - In the left tree panel, expand "ARE - Areas"
   - Chapter 1 (Irenicus Dungeon) areas start with "AR06":
     - AR0602 - Starting cell
     - AR0603 - Golem room
     - AR0604 - Library
     - AR0605 - Portal room
     - AR0606 - Dryads level
     - ... (etc.)

3. **Open an Area**
   - Click on "AR0602.ARE" (starting area)

4. **View Creatures Tab**
   - In the main panel, find the "Actors" or "Creatures" section
   - This lists all NPCs/creatures in that area

5. **Export Method 1: Manual List**
   - Copy creature names (e.g., "Imoen", "Duergar1", "Golem02")
   - Paste into a text file: `C:\Users\tenod\source\repos\BG2 Voiceover\exports\chapter1_npcs.txt`

6. **Export Method 2: View as Table**
   - Right-click on "Actors" section
   - Choose "View as Table" or "Export"
   - Save as: `C:\Users\tenod\source\repos\BG2 Voiceover\exports\AR0602_actors.csv`

7. **Repeat for all Chapter 1 areas**

**Expected Result:** A list of NPCs per area, like:
```
Area,CreatureName,CreatureFile
AR0602,Imoen,IMOEN2
AR0602,Duergar Guard,DUERGA01
AR0603,Clay Golem,GOLEM02
```

---

## Part 4: Export CRE Files (Creature Details)

**Purpose:** Get metadata about each NPC (race, class, gender, alignment) to design voices.

### Steps:

1. **Still in Near Infinity**

2. **Find Creature Files**
   - In the left tree panel, expand "CRE - Creatures"
   - Search for a specific creature (Ctrl+F) like "IMOEN"

3. **Open the CRE File**
   - Click on "IMOEN2.CRE" or similar

4. **View Details**
   - In the main panel, you'll see:
     - Gender: Female
     - Race: Human
     - Class: Thief
     - Alignment: Chaotic Good
     - Sound Set: IMOEN2
     - Animation: MAGE_FEMALE

5. **Export Method: Take Notes**
   - Unfortunately, CRE files don't export cleanly to CSV
   - **Solution:** I'll create a script to parse CRE files automatically
   - For now, just note the important ones manually

**Alternative:** Export all CRE as text, then I'll parse them:
- Right-click on "CRE - Creatures" folder
- Export All → Text Format
- Save to: `C:\Users\tenod\source\repos\BG2 Voiceover\exports\cre\`

---

## Quick Reference: What to Export for Chapter 1

**Minimum exports needed:**

1. ✅ **dialog.tlk** → `exports/dialog_tlk.csv` (one-time, 5 minutes)
2. ✅ **Chapter 1 DLG files** → `exports/dlg/*.csv` (10-20 files, 10 minutes)
3. ✅ **Chapter 1 area lists** → `exports/chapter1_npcs.txt` (manual list, 15 minutes)

**Optional but helpful:**

4. ⚙️ **All CRE files** → `exports/cre/*.txt` (for voice auto-suggest, 10 minutes)

---

## After Export: What Happens Next

Once you've exported the files, run:

```powershell
# 1) Turn the .D files into *_dlg.csv under exports/ni/
py scripts\convert_d_to_csv.py

# 2) Join TLK + DLG into data/lines.csv (auto-detects dialog.tlk)
py scripts\near_infinity_join.py

# 3) Inspect status / next actions
py scripts\character_lib.py status
```

I'll process everything automatically from there.

---

## Troubleshooting

**"Can't find dialog.tlk"**
- Make sure you opened the correct game folder in Near Infinity
- Look for "TLK Files" in the left tree panel

**"Export button is grayed out"**
- Make sure you've selected/opened a specific file first
- Try right-clicking instead of using the menu

**"Export is too slow"**
- For large exports (all DLG files), go get coffee - it takes 10-20 minutes
- You can cancel and export just specific files you need

**"I don't see CSV option"**
- Some versions use "TSV" (Tab-Separated Values) instead
- That works fine - just save as .csv extension anyway

---

## Summary

**Total time investment:** 30-60 minutes per chapter
**Automation benefit:** Saves days of manual work

After you export once, I handle:
- ✅ Parsing and joining data
- ✅ Voice suggestions
- ✅ Reference creation
- ✅ Batch synthesis
- ✅ QA checking
- ✅ Deployment

**Your work:** 1 hour of exports
**My work:** 100+ hours of automation

Worth it? 😊
