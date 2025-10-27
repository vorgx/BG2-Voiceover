import csv
import json
import subprocess
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from bg2vo.config import load_config  # type: ignore[import-not-found]
from bg2vo.voices import load_voices  # type: ignore[import-not-found]
from bg2vo.emotions import detect_emotion, get_emotion_config  # type: ignore[import-not-found]

# Try to load config, fallback to hardcoded paths
try:
    settings = load_config()
    LINES = Path(settings.inputs.get("lines_csv", "data/lines.csv"))
    if not LINES.is_absolute():
        LINES = ROOT / LINES
    VOICES_PATH = Path(settings.inputs.get("voices_json", "data/voices.json"))
    if not VOICES_PATH.is_absolute():
        VOICES_PATH = ROOT / VOICES_PATH
    OUT = Path(settings.outputs.get("ogg_dir", "build/OGG"))
    if not OUT.is_absolute():
        OUT = ROOT / OUT
    INDEX_TTS_ROOT = Path(settings.paths.get("index_tts_root", r"C:\Users\tenod\source\repos\TTS\index-tts"))
    INDEX_TTS_BIN = settings.index_tts.get("executable", str(INDEX_TTS_ROOT / ".venv" / "Scripts" / "indextts.exe"))
    INDEX_TTS_CONFIG = settings.index_tts.get("config", str(INDEX_TTS_ROOT / "checkpoints" / "config.yaml"))
except Exception as e:
    print(f"⚠️ Config load failed ({e}), using defaults")
    LINES = ROOT / "data" / "lines.csv"
    VOICES_PATH = ROOT / "data" / "voices.json"
    OUT = ROOT / "build" / "OGG"
    INDEX_TTS_ROOT = Path(r"C:\Users\tenod\source\repos\TTS\index-tts")
    INDEX_TTS_BIN = str(INDEX_TTS_ROOT / ".venv" / "Scripts" / "indextts.exe")
    INDEX_TTS_CONFIG = str(INDEX_TTS_ROOT / "checkpoints" / "config.yaml")

OUT.mkdir(parents=True, exist_ok=True)

COMMON_ARGS: list[str] = ["-c", INDEX_TTS_CONFIG]

TOKEN_REPLACEMENTS = {
    "CHARNAME": "you",
    "PRO_HESHE": "they",
    "PRO_HIMHER": "them",
    "PRO_HISHER": "their",
    "PRO_MANWOMAN": "person",
    "PRO_LADYLORD": "my friend",
    "LADYLORD": "friend",
    "PRO_RACE": "traveler",
    "RACE": "traveler",
    "PRO_SIRMAAM": "friend",
    "SIRMAAM": "friend",
    "MALEFEMALE": "person",
    "PRO_MALEFEMALE": "person",
    "MANWOMAN": "person",
    "PRO_BROTHERSISTER": "friend",
    "BROTHERSISTER": "friend",
    "PRO_GIRLBOY": "child",
    "GIRLBOY": "child",
    "GABBER": "friend",
    "DAYNIGHTALL": "day",
}

TOKEN_PATTERN = re.compile(r"<([^>]+)>")


def sanitize(text: str) -> str:
    """Normalize dialogue text by removing WeiDU tokens and tidying spacing."""

    def _replace(match: re.Match[str]) -> str:
        token = match.group(1)
        if token == "CHARNAME":
            return "__CHARNAME__"
        return TOKEN_REPLACEMENTS.get(token, "")

    cleaned = TOKEN_PATTERN.sub(_replace, text)
    cleaned = cleaned.replace("~", "")
    cleaned = cleaned.replace("\u00a0", " ")
    fallback = cleaned.replace("__CHARNAME__", "you").strip()
    # Normalize stray mojibake dashes that appear in exports
    cleaned = cleaned.replace("â€”", "—").replace("â€“", "—")

    # Remove direct-address placeholders before replacing final token
    cleaned = re.sub(r"(^|[.!?]\s*)__CHARNAME__,\s*", r"\1", cleaned)
    cleaned = re.sub(r"(^|[.!?]\s*)__CHARNAME__\s*[!?]+\s*", r"\1", cleaned)
    cleaned = re.sub(r",\s*__CHARNAME__\s*,", ", ", cleaned)
    cleaned = re.sub(r",\s*__CHARNAME__([.!?])", r"\1", cleaned)
    cleaned = re.sub(r",\s*__CHARNAME__", "", cleaned)

    cleaned = cleaned.replace("__CHARNAME__", "you")
    cleaned = re.sub(r"^(?:[Yy]ou[!?]+\s+)+", "", cleaned)
    cleaned = re.sub(r"^[\s\-—]*[,.;:!?]+\s*", "", cleaned)
    cleaned = cleaned.lstrip('\"')
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"\s+([,.!?;:])", r"\1", cleaned)
    cleaned = re.sub(r",\s*,", ", ", cleaned)
    cleaned = re.sub(r"(?<!\.)\.\.(?!\.)", ".", cleaned)
    cleaned = re.sub(r"([!?;:]){2,}", lambda m: m.group(0)[0], cleaned)
    cleaned = re.sub(r",([!?;:])", r"\1", cleaned)

    for pattern, replacement in (
        (r"\b[Yy]ou has\b", "you have"),
        (r"\b[Yy]ou is\b", "you are"),
        (r"\b[Yy]ou was\b", "you were"),
        (r"\b[Yy]ou's\b", "your"),
        (r"\b[Tt]hey has\b", "they have"),
        (r"\b[Tt]hey is\b", "they are"),
        (r"\b[Tt]hey was\b", "they were"),
        (r"\b[Tt]hey decides\b", "they decide"),
    ):
        cleaned = re.sub(pattern, replacement, cleaned)

    cleaned = cleaned.strip()
    if not cleaned:
        cleaned = fallback
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned


with open(VOICES_PATH, "r", encoding="utf-8") as voice_file:
    VOICE_MAP = json.load(voice_file)


def synth_one(strref: str, speaker: str, text: str, manual_emotion: str | None = None) -> None:
    voice_config = VOICE_MAP.get(speaker, VOICE_MAP.get("_default_", {"voice": "narrator"}))
    out_wav = OUT / f"{strref}.wav"
    if out_wav.exists():
        return

    sanitized = sanitize(text)
    if not sanitized:
        return

    # Handle both old string format and new dict format
    if isinstance(voice_config, str):
        # Legacy: just a voice name or ref path
        voice_ref = voice_config
        config_dict = {"voice": voice_ref}
    elif isinstance(voice_config, dict):
        voice_ref = voice_config.get("ref") or voice_config.get("voice", "narrator")
        config_dict = dict(voice_config)
    else:
        voice_ref = "narrator"
        config_dict = {"voice": "narrator"}
    
    # Convert relative voice reference path to absolute
    voice_ref_path = Path(voice_ref)
    if not voice_ref_path.is_absolute() and voice_ref_path.suffix == ".wav":
        voice_ref = str(ROOT / voice_ref_path)

    # EMOTION DETECTION: Use manual emotion if provided, auto-detect for Ilyich only
    if manual_emotion and manual_emotion.strip():
        emotion = manual_emotion.strip().lower()
        print(f"  🎭 Manual emotion: {emotion}")
        emotion_config = get_emotion_config(emotion, speaker)
    elif speaker.lower() == "ilyich":
        # Auto-detect emotion for Ilyich to make him more aggressive
        emotion = detect_emotion(text)
        print(f"  🎭 Auto-detected emotion for Ilyich: {emotion}")
        emotion_config = get_emotion_config(emotion, speaker)
    else:
        # Skip auto-detection for other speakers
        emotion_config = None
    
    # Merge emotion config with voice config (emotion takes precedence)
    if emotion_config:
        # Convert relative emotion paths to absolute paths
        if "emo_audio_prompt" in emotion_config:
            emo_path = Path(emotion_config["emo_audio_prompt"])
            if not emo_path.is_absolute():
                emotion_config["emo_audio_prompt"] = str(ROOT / emo_path)
        
        config_dict.update(emotion_config)
        print(f"  🎭 Using emotion: {emotion}")
    
    # If we have advanced params, use Python API instead of CLI
    # Check if we need to use API (for any advanced parameters)
    use_api = any(k in config_dict for k in ["emo_alpha", "emo_audio_prompt", "emo_vector", "emo_text", "interval_silence", "use_random", "speed", "pitch", "pitch_shift"])

    if use_api:
        # Use Python API for advanced parameters
        synth_with_api(strref, voice_ref, config_dict, sanitized, out_wav)
    else:
        # Use CLI for simple cases
        args = [
            INDEX_TTS_BIN,
            *COMMON_ARGS,
            "-d", "cuda",  # Use CUDA GPU for faster inference
            "-v",
            voice_ref,
            "-o",
            str(out_wav),
            sanitized,
        ]
        print("Generating:", strref, "->", out_wav)
        subprocess.run(args, check=True, cwd=INDEX_TTS_ROOT)


def synth_with_api(strref: str, voice_ref: str, config: dict, text: str, out_wav: Path) -> None:
    """Use Index-TTS Python API for advanced parameters via subprocess"""
    # Create a temporary Python script to run in Index-TTS environment
    import tempfile
    import json as json_mod
    
    # Extract pitch_shift for post-processing (API doesn't support it directly)
    pitch_shift = config.get("pitch_shift")
    speed_adjust = config.get("speed")
    
    script_content = f'''
import sys
sys.path.insert(0, r"{INDEX_TTS_ROOT}")
from indextts.infer_v2 import IndexTTS2
import subprocess

# Initialize TTS
import subprocess as sp
try:
    result = sp.run(["nvidia-smi"], capture_output=True)
    has_cuda = result.returncode == 0
except:
    has_cuda = False

tts = IndexTTS2(
    cfg_path=r"{INDEX_TTS_ROOT / "checkpoints" / "config.yaml"}",
    model_dir=r"{INDEX_TTS_ROOT / "checkpoints"}",
    use_fp16=False,
    device="cuda:0" if has_cuda else "cpu"
)

# Run inference
config = {json_mod.dumps(config)}
kwargs = {{
    "spk_audio_prompt": r"{voice_ref}",
    "text": {repr(text)},
    "output_path": r"{out_wav}",
    "verbose": False,
    "num_beams": 1,
    "do_sample": False,
}}

# Add optional parameters (exclude pitch_shift and speed - handled as post-processing)
if "emo_audio_prompt" in config:
    kwargs["emo_audio_prompt"] = config["emo_audio_prompt"]
if "emo_alpha" in config:
    kwargs["emo_alpha"] = config["emo_alpha"]
if "emo_vector" in config:
    kwargs["emo_vector"] = config["emo_vector"]
if "emo_text" in config:
    kwargs["use_emo_text"] = True
    kwargs["emo_text"] = config["emo_text"]
if "interval_silence" in config:
    kwargs["interval_silence"] = config["interval_silence"]
if "use_random" in config:
    kwargs["use_random"] = config["use_random"]
if "max_text_tokens_per_segment" in config:
    kwargs["max_text_tokens_per_segment"] = config["max_text_tokens_per_segment"]

tts.infer(**kwargs)
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(script_content)
        temp_script = f.name
    
    try:
        print(f"  Generating (API): {strref} -> {out_wav}")
        # Run the script using Index-TTS's Python environment
        index_python = INDEX_TTS_ROOT / ".venv" / "Scripts" / "python.exe"
        result = subprocess.run([str(index_python), temp_script], 
                              capture_output=True, text=True, cwd=INDEX_TTS_ROOT)
        if result.returncode != 0:
            print(f"  ⚠️ API mode failed: {result.stderr}")
            print(f"  Falling back to CLI")
            args = [
                INDEX_TTS_BIN,
                *COMMON_ARGS,
                "-v",
                voice_ref,
                "-o",
                str(out_wav),
                text,
            ]
            subprocess.run(args, check=True, cwd=INDEX_TTS_ROOT)
        
        # Apply post-processing if needed
        if pitch_shift or speed_adjust:
            print(f"  🎵 Applying post-processing (pitch_shift={pitch_shift}, speed={speed_adjust})")
            sys.path.insert(0, str(ROOT / "scripts" / "utils"))
            from adjust_audio import change_pitch, change_speed
            import soundfile as sf
            import scipy.io.wavfile as wavfile
            
            # Load generated audio
            sr, audio = wavfile.read(str(out_wav))
            
            # Apply speed adjustment
            if speed_adjust and speed_adjust != 1.0:
                audio, sr = change_speed(audio, sr, speed_adjust)
            
            # Apply pitch shift
            if pitch_shift:
                audio = change_pitch(audio, sr, pitch_shift)
            
            # Save modified audio
            wavfile.write(str(out_wav), sr, audio)
            
    finally:
        import os
        try:
            os.unlink(temp_script)
        except:
            pass


def synth_all(input_csv: Path | None = None) -> None:
    """Synthesize every line from the specified CSV (defaults to data/lines.csv)."""
    csv_path = input_csv or LINES
    if not csv_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {csv_path}")
    
    print(f"📄 Reading lines from: {csv_path}")
    with open(csv_path, newline="", encoding="utf-8") as lines_file:
        reader = csv.DictReader(lines_file)
        for row in reader:
            # Check if there's a manual Emotion column
            manual_emotion = row.get("Emotion", None)
            synth_one(row["StrRef"], row["Speaker"], row["Text"], manual_emotion)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Synthesize dialogue lines using Index-TTS")
    parser.add_argument("--input", type=Path, help="Input CSV file (default: data/lines.csv)")
    parser.add_argument("--chapter", type=int, help="Chapter number (uses data/chapterN_lines.csv)")
    args = parser.parse_args()
    
    input_path = None
    if args.chapter:
        input_path = ROOT / "data" / f"chapter{args.chapter}_lines.csv"
        print(f"🎯 Synthesizing Chapter {args.chapter}")
    elif args.input:
        input_path = args.input
    
    synth_all(input_path)
