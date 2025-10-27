"""Verify mod installation in BG2EE."""
from pathlib import Path

GAME_DIR = Path(r"E:\SteamLibrary\steamapps\common\Baldur's Gate II Enhanced Edition")
OVERRIDE = GAME_DIR / "override"

print("🔍 Checking mod installation...\n")

# Check if game directory exists
if not GAME_DIR.exists():
    print(f"❌ Game directory not found: {GAME_DIR}")
    exit(1)

print(f"✅ Game directory found: {GAME_DIR}")

# Check override folder
if not OVERRIDE.exists():
    print(f"❌ Override folder not found: {OVERRIDE}")
    exit(1)

print(f"✅ Override folder found: {OVERRIDE}")

# Check for our WAV files
wav_files = ["OH38537.wav", "OH38606.wav"]
installed = []
missing = []

for wav in wav_files:
    path = OVERRIDE / wav
    if path.exists():
        size_kb = path.stat().st_size / 1024
        installed.append((wav, size_kb))
        print(f"✅ {wav} installed ({size_kb:.1f} KB)")
    else:
        missing.append(wav)
        print(f"❌ {wav} NOT FOUND")

# Check WeiDU installation log
weidu_log = GAME_DIR / "WeiDU.log"
if weidu_log.exists():
    print(f"\n📋 WeiDU.log contents:")
    print("-" * 60)
    print(weidu_log.read_text(encoding="utf-8"))
    print("-" * 60)
else:
    print(f"\n⚠️ WeiDU.log not found")

# Summary
print(f"\n{'='*60}")
if len(installed) == len(wav_files):
    print("🎉 SUCCESS! All test files installed correctly.")
    print("\n🎮 Ready to test in-game:")
    print("   1. Launch BG2EE")
    print("   2. Start new game or load Irenicus Dungeon save")
    print("   3. Find Imoen and listen for voiced dialogue")
elif len(installed) > 0:
    print(f"⚠️ PARTIAL: {len(installed)}/{len(wav_files)} files installed")
    print(f"   Missing: {', '.join(missing)}")
else:
    print("❌ FAILED: No files installed")
    print("\nTry manual installation:")
    print(f'   cd "{GAME_DIR}"')
    print("   .\\setup-vvoBG.exe")
print(f"{'='*60}")
