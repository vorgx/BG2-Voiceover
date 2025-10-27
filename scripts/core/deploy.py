"""Deploy generated WAV files to WeiDU mod structure.

This script:
1. Copies WAV files from build/OGG to mod/vvoBG/OGG
2. Renames them with OH prefix (WeiDU convention: OH<StrRef>.wav)
3. Generates WeiDU TP2 script entries for testing

Usage:
    python scripts/deploy.py --test       # Deploy only test files
    python scripts/deploy.py --chapter 1  # Deploy all Chapter 1
    python scripts/deploy.py --all        # Deploy everything in build/OGG
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD_OGG = ROOT / "build" / "OGG"
MOD_OGG = ROOT / "mod" / "vvoBG" / "OGG"
TP2_FILE = ROOT / "mod" / "vvoBG.tp2"


def deploy_files(strrefs: list[str] | None = None) -> list[tuple[str, Path]]:
    """Deploy WAV files to mod directory.
    
    Args:
        strrefs: List of specific StrRefs to deploy, or None for all
        
    Returns:
        List of (strref, deployed_path) tuples
    """
    MOD_OGG.mkdir(parents=True, exist_ok=True)
    
    deployed = []
    wav_files = list(BUILD_OGG.glob("*.wav"))
    
    if not wav_files:
        print("⚠️ No WAV files found in build/OGG")
        return deployed
    
    for wav_path in wav_files:
        # Extract StrRef from filename
        strref = wav_path.stem
        
        # Filter if specific strrefs requested
        if strrefs and strref not in strrefs:
            continue
        
        # WeiDU convention: OH<StrRef>.wav
        target_name = f"OH{strref}.wav"
        target_path = MOD_OGG / target_name
        
        # Copy file
        shutil.copy2(wav_path, target_path)
        deployed.append((strref, target_path))
        print(f"✅ Deployed: {strref}.wav → {target_name}")
    
    return deployed


def generate_tp2_entries(deployed: list[tuple[str, Path]]) -> str:
    """Generate WeiDU TP2 script entries for deployed files."""
    lines = [
        "// Auto-generated voice entries",
        "BEGIN ~BG2 Voiceover - Test~",
        "",
    ]
    
    for strref, path in deployed:
        lines.append(f"// StrRef {strref}")
        lines.append(f'COPY ~vvoBG/OGG/OH{strref}.wav~ ~override~')
        lines.append(f"STRING_SET {strref} @{strref}")
        lines.append("")
    
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy WAV files to WeiDU mod")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--test", action="store_true", help="Deploy test files only (38537, 38606)")
    group.add_argument("--chapter", type=int, help="Deploy all Chapter N files")
    group.add_argument("--all", action="store_true", help="Deploy all files in build/OGG")
    parser.add_argument("--generate-tp2", action="store_true", help="Generate TP2 script entries")
    args = parser.parse_args()
    
    # Determine which files to deploy
    strrefs = None
    if args.test:
        strrefs = ["38537", "38606"]
        print("🎯 Deploying test files only...")
    elif args.chapter:
        print(f"🎯 Deploying Chapter {args.chapter} files...")
        # For now, deploy all (could filter by chapter later)
    elif args.all:
        print("🎯 Deploying all files...")
    else:
        # Default to test mode
        strrefs = ["38537", "38606"]
        print("🎯 No mode specified, deploying test files...")
    
    # Deploy
    deployed = deploy_files(strrefs)
    
    if not deployed:
        print("❌ No files were deployed")
        return
    
    print(f"\n✅ Deployed {len(deployed)} files to {MOD_OGG}")
    
    # Generate TP2 entries if requested
    if args.generate_tp2:
        tp2_content = generate_tp2_entries(deployed)
        output_file = ROOT / "mod" / "vvoBG_generated.tp2"
        output_file.write_text(tp2_content, encoding="utf-8")
        print(f"\n📝 Generated WeiDU script: {output_file}")
        print("\nAdd this to your main TP2 file:")
        print("-" * 60)
        print(tp2_content[:500])
        if len(tp2_content) > 500:
            print("... (truncated)")
    
    print("\n📦 Next steps:")
    print("1. Copy mod/vvoBG folder to your BG2EE directory")
    print("2. Update mod/vvoBG.tp2 with the deployed StrRefs")
    print("3. Run setup-vvoBG.exe in the game directory")
    print("4. Launch game and test dialogue")


if __name__ == "__main__":
    main()
