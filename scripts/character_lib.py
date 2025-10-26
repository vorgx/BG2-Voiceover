"""
Character Library Management Tool

View, update, and analyze character voice tracking data.
"""
import csv
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
CHARACTERS_CSV = ROOT / "data" / "characters.csv"

def load_characters():
    """Load characters.csv into list of dicts"""
    with open(CHARACTERS_CSV, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def save_characters(characters):
    """Save characters back to CSV"""
    if not characters:
        return
    
    fieldnames = characters[0].keys()
    with open(CHARACTERS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(characters)

def show_status():
    """Display character status summary"""
    chars = load_characters()
    
    print("=" * 70)
    print("CHARACTER VOICE LIBRARY - STATUS")
    print("=" * 70)
    print()
    
    # Count by status
    status_counts = Counter(c['Status'] for c in chars)
    print("📊 By Status:")
    for status, count in sorted(status_counts.items()):
        print(f"   {status:15s}: {count:2d}")
    print()
    
    # Show by phase
    print("📋 Phase 1 - Core Companions:")
    phase1 = ['Imoen', 'Minsc', 'Jaheira', 'Viconia', 'Edwin']
    for char in chars:
        if char['Canonical'] in phase1:
            status_icon = "✅" if char['Status'] == "Locked" else "⏳"
            ref_info = "multi-ref" if "multi" in char['RefFile'] else (char['VoicePreset'] or "none")
            print(f"   {status_icon} {char['Canonical']:15s} {char['Status']:12s} {ref_info}")
    print()
    
    print("📋 Phase 2 - Extended Companions:")
    phase2 = ['Aerie', 'Korgan', 'Anomen', 'Keldorn', 'Nalia', 'HaerDalis']
    for char in chars:
        if char['Canonical'] in phase2:
            status_icon = "✅" if char['Status'] == "Locked" else "📝"
            ref_info = char['VoicePreset'] or "needs work"
            print(f"   {status_icon} {char['Canonical']:15s} {char['Status']:12s} {ref_info}")
    print()
    
    # Next actions
    pending = [c for c in chars if c['Status'] == 'Pending']
    if pending:
        print(f"🎯 Next: Complete {len(pending)} pending characters")
        for char in pending[:3]:
            print(f"   → {char['Canonical']}: Create multi-reference, test, lock")
    
    print("=" * 70)

def show_character(name):
    """Display detailed info for one character"""
    chars = load_characters()
    char = next((c for c in chars if c['Canonical'].lower() == name.lower()), None)
    
    if not char:
        print(f"❌ Character '{name}' not found")
        return
    
    print("=" * 70)
    print(f"CHARACTER: {char['Canonical']}")
    print("=" * 70)
    print()
    
    print("Identity:")
    print(f"  Canonical:  {char['Canonical']}")
    print(f"  Aliases:    {char['Aliases']}")
    print(f"  DLG Files:  {char['DLGFiles']}")
    print()
    
    print("Voice Characteristics:")
    print(f"  Gender:     {char['Gender']}")
    print(f"  Age Band:   {char['AgeBand']}")
    print(f"  Archetype:  {char['Archetype']}")
    print(f"  Energy:     {char['Energy']}")
    print(f"  Timbre:     {char['Timbre']}")
    print(f"  Accent:     {char['Accent']}")
    print()
    
    print("Implementation:")
    print(f"  Voice:      {char['HasCanonicalVoice']} canonical voice")
    print(f"  Preset:     {char['VoicePreset'] or '(none)'}")
    print(f"  Reference:  {char['RefFile'] or '(none)'}")
    print(f"  Status:     {char['Status']}")
    print()
    
    if char['Notes']:
        print(f"Notes: {char['Notes']}")
        print()
    
    print("=" * 70)

def update_status(name, new_status):
    """Update character status"""
    valid_statuses = ['Draft', 'Pending', 'Auditioned', 'Locked']
    if new_status not in valid_statuses:
        print(f"❌ Invalid status. Must be one of: {', '.join(valid_statuses)}")
        return
    
    chars = load_characters()
    char = next((c for c in chars if c['Canonical'].lower() == name.lower()), None)
    
    if not char:
        print(f"❌ Character '{name}' not found")
        return
    
    old_status = char['Status']
    char['Status'] = new_status
    save_characters(chars)
    
    print(f"✅ {char['Canonical']}: {old_status} → {new_status}")

def list_pending():
    """Show all pending characters"""
    chars = load_characters()
    pending = [c for c in chars if c['Status'] == 'Pending']
    
    if not pending:
        print("✅ No pending characters")
        return
    
    print("=" * 70)
    print(f"PENDING CHARACTERS ({len(pending)})")
    print("=" * 70)
    print()
    
    for char in pending:
        print(f"• {char['Canonical']}")
        print(f"  {char['Gender']}/{char['AgeBand']}/{char['Archetype']} - {char['Energy']} energy, {char['Timbre']} timbre")
        print(f"  Preset: {char['VoicePreset'] or '(none)'}")
        print(f"  Reference: {char['RefFile'] or '(none)'}")
        print()

def needs_reference():
    """Show characters that need multi-references created"""
    chars = load_characters()
    needs = [c for c in chars if c['Status'] in ['Pending', 'Auditioned'] and not c['RefFile']]
    
    if not needs:
        print("✅ All active characters have references")
        return
    
    print("=" * 70)
    print(f"CHARACTERS NEEDING MULTI-REFERENCES ({len(needs)})")
    print("=" * 70)
    print()
    
    for char in needs:
        print(f"• {char['Canonical']}")
        print(f"  Find: {char['Aliases']} in BG2 Files/WAV Files/")
        print(f"  Voice: {char['Archetype']} {char['Gender']}, {char['Energy']} energy")
        print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/character_lib.py status              # Show summary")
        print("  python scripts/character_lib.py show CHARACTER      # Show character details")
        print("  python scripts/character_lib.py pending             # List pending")
        print("  python scripts/character_lib.py needs-ref           # List needing references")
        print("  python scripts/character_lib.py update CHARACTER STATUS  # Update status")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        show_status()
    elif command == "show" and len(sys.argv) > 2:
        show_character(sys.argv[2])
    elif command == "pending":
        list_pending()
    elif command == "needs-ref":
        needs_reference()
    elif command == "update" and len(sys.argv) > 3:
        update_status(sys.argv[2], sys.argv[3])
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
