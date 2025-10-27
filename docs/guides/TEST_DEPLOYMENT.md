# Test Deployment Guide

## ✅ Step 1: Generate Audio (COMPLETE)
- Generated 2 test WAV files:
  - `38537.wav` (245 KB) - Imoen: "I can help you too..."
  - `38606.wav` (411 KB) - Imoen: "Wow, a golem..."

## ✅ Step 2: Deploy to Mod (COMPLETE)
```powershell
python scripts/deploy.py --test --generate-tp2
```
- Copied to `mod/vvoBG/OGG/` with OH prefix
- Generated WeiDU TP2 entries

## ✅ Step 3: Copy to Game Directory (COMPLETE)
```powershell
$gameDir = "E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition"
Copy-Item -Path "mod\*" -Destination $gameDir -Recurse -Force
```

## 🎯 Step 4: Install Mod with WeiDU

**Manual Installation (Recommended for Testing):**

1. Open PowerShell as Administrator
2. Navigate to game directory:
   ```powershell
   cd "E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition"
   ```

3. Uninstall previous version (if exists):
   ```powershell
   .\setup-vvoBG.exe --uninstall
   ```

4. Install new version:
   ```powershell
   .\setup-vvoBG.exe
   ```
   - Press `I` to install
   - Select component `0` (Test)
   - Press `Enter` to continue
   - Wait for "INSTALLED" message

5. Verify installation:
   ```powershell
   Get-ChildItem override\OH38*.wav
   ```
   Should show:
   - `OH38537.wav` (245 KB)
   - `OH38606.wav` (411 KB)

## 🎮 Step 5: Test In-Game

### Where to Find These Lines:

**StrRef 38537** - Imoen: "I can help you too..."
- **Location**: Irenicus Dungeon, after finding Minsc/Jaheira
- **Trigger**: Talk to Imoen after freeing her

**StrRef 38606** - Imoen: "Wow, a golem..."
- **Location**: Irenicus Dungeon, golem room
- **Trigger**: Talk to Imoen near the neutral golem

### Testing Steps:

1. Launch BG2EE
2. Start new game or load save in Irenicus Dungeon
3. Find Imoen (cell area after escaping your starting room)
4. Trigger the dialogue
5. **Listen for voiced lines** - should hear Imoen's TTS voice

### What to Check:

- [ ] Voice plays (not silent)
- [ ] Voice matches Imoen's character
- [ ] No audio glitches/pops
- [ ] Subtitles match audio
- [ ] Text doesn't have `<CHARNAME>` or other tokens
- [ ] Volume appropriate (not too loud/quiet)

## 🔧 Troubleshooting

### No Audio Plays
- Check `override\` folder contains OH38537.wav and OH38606.wav
- Verify WAV files aren't corrupted (should be ~245KB and ~411KB)
- Check game audio settings (voice volume not muted)

### Wrong Line Plays
- WeiDU STRING_SET may have failed
- Check SETUP-VVOBG.DEBUG for errors
- Try reinstalling: `.\setup-vvoBG.exe --reinstall`

### Mod Won't Install
- Close BG2EE if running
- Delete `vvoBG/backup` folder
- Try: `.\setup-vvoBG.exe --force-install 0`

## ✅ Success Criteria

If you hear Imoen's synthesized voice for either line in-game:
- **The entire pipeline works end-to-end!**
- You can proceed to generate full Chapter 1 (907 lines)
- Voice quality can be refined with better references

## 📊 Next Steps After Successful Test

1. Create proper voice references for all Chapter 1 speakers
2. Run full synthesis: `python scripts/synth.py --chapter 1`
3. Deploy Chapter 1: `python scripts/deploy.py --chapter 1`
4. Update TP2 for all 907 lines (automation TBD)
5. Test in-game thoroughly

## 🎉 If It Works

You've successfully validated:
- ✅ Text sanitization (token removal)
- ✅ TTS synthesis with Index-TTS
- ✅ WeiDU packaging
- ✅ In-game audio playback
- ✅ End-to-end automation pipeline

**The framework is proven!** Scale to full chapter when ready.
