import csv
import json
import subprocess
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINES = ROOT / "data" / "lines.csv"
VOICES = ROOT / "data" / "voices.json"
OUT = ROOT / "build" / "OGG"
OUT.mkdir(parents=True, exist_ok=True)

# Point directly to the venv CLI so we do not rely on PATH or activation
INDEX_TTS_ROOT = Path(r"C:\\Users\\tenod\\source\\repos\\TTS\\index-tts")
INDEX_TTS_BIN = str(INDEX_TTS_ROOT / ".venv" / "Scripts" / "indextts.exe")
COMMON_ARGS: list[str] = [
    "-c",
    str(INDEX_TTS_ROOT / "checkpoints" / "config.yaml"),
]


def sanitize(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", "", text)
    cleaned = cleaned.replace("~", "").strip()
    return cleaned


with open(VOICES, "r", encoding="utf-8") as voice_file:
    VOICE_MAP = json.load(voice_file)


def synth_one(strref: str, speaker: str, text: str) -> None:
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
        use_api = False
    elif isinstance(voice_config, dict):
        voice_ref = voice_config.get("ref") or voice_config.get("voice", "narrator")
        # If we have advanced params, use Python API instead of CLI
        use_api = any(k in voice_config for k in ["emo_alpha", "emo_audio_prompt", "emo_text", "interval_silence", "use_random"])
    else:
        voice_ref = "narrator"
        use_api = False

    if use_api:
        # Use Python API for advanced parameters
        synth_with_api(strref, voice_ref, voice_config, sanitized, out_wav)
    else:
        # Use CLI for simple cases
        args = [
            INDEX_TTS_BIN,
            *COMMON_ARGS,
            "-v",
            voice_ref,
            "-o",
            str(out_wav),
            sanitized,
        ]
        print("Generating:", strref, "->", out_wav)
        subprocess.run(args, check=True, cwd=INDEX_TTS_ROOT)


def synth_with_api(strref: str, voice_ref: str, config: dict, text: str, out_wav: Path) -> None:
    """Use Index-TTS Python API for advanced parameters"""
    import sys
    sys.path.insert(0, str(INDEX_TTS_ROOT))
    
    from indextts.infer_v2 import IndexTTS2
    
    print("Generating (API):", strref, "->", out_wav)
    
    # Initialize TTS (expensive, but needed for advanced features)
    tts = IndexTTS2(
        cfg_path=str(INDEX_TTS_ROOT / "checkpoints" / "config.yaml"),
        model_dir=str(INDEX_TTS_ROOT / "checkpoints"),
        use_fp16=False,
        device="cuda:0" if subprocess.run(["nvidia-smi"], capture_output=True).returncode == 0 else "cpu"
    )
    
    # Extract advanced parameters
    kwargs = {
        "spk_audio_prompt": voice_ref,
        "text": text,
        "output_path": str(out_wav),
        "verbose": False,
        "num_beams": 1,
        "do_sample": False,
    }
    
    # Add optional parameters if present
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
    
    # Run inference
    tts.infer(**kwargs)


with open(LINES, newline="", encoding="utf-8") as lines_file:
    reader = csv.DictReader(lines_file)
    for row in reader:
        synth_one(row["StrRef"], row["Speaker"], row["Text"])
