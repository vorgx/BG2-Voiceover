"""Batch synthesis script that keeps Index-TTS models loaded in memory.

Much faster than the legacy per-line subprocess approach in synth.py.
"""
from __future__ import annotations

import argparse
import csv
import importlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import scipy.io.wavfile as wavfile
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from bg2vo.config import load_config  # type: ignore[import-not-found]
from bg2vo.emotions import detect_emotion, get_emotion_config  # type: ignore[import-not-found]
# Audio post-processing helpers
sys.path.insert(0, str(ROOT / "scripts" / "utils"))
from adjust_audio import change_pitch, change_speed  # type: ignore[import]
# Vocalization detection
from classify_vocalizations import classify_text, VocalizationType  # type: ignore[import]
# Statistics auto-update
from update_project_stats import main as update_stats  # type: ignore[import]

# ---------------------------------------------------------------------------
# Configuration loading (mirrors synth.py defaults)
# ---------------------------------------------------------------------------
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
    INDEX_TTS_ROOT = Path(settings.paths.get("index_tts_root", r"C:\\Users\\tenod\\source\\repos\\TTS\\index-tts"))
    INDEX_TTS_CONFIG = settings.index_tts.get("config", str(INDEX_TTS_ROOT / "checkpoints" / "config.yaml"))
except Exception as exc:  # pragma: no cover - defensive fallback
    print(f"⚠️ Config load failed ({exc}), using defaults")
    LINES = ROOT / "data" / "lines.csv"
    VOICES_PATH = ROOT / "data" / "voices.json"
    OUT = ROOT / "build" / "OGG"
    INDEX_TTS_ROOT = Path(r"C:\\Users\\tenod\\source\\repos\\TTS\\index-tts")
    INDEX_TTS_CONFIG = str(INDEX_TTS_ROOT / "checkpoints" / "config.yaml")

OUT.mkdir(parents=True, exist_ok=True)

with open(VOICES_PATH, "r", encoding="utf-8") as voice_file:
    VOICE_MAP: dict[str, dict[str, object] | str] = json.load(voice_file)

# ---------------------------------------------------------------------------
# Text sanitiser (copied from synth.py)
# ---------------------------------------------------------------------------
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

    cleaned = re.sub(r"(^|[.!?]\s*)__CHARNAME__,\s*", r"\1", cleaned)
    cleaned = re.sub(r"(^|[.!?]\s*)__CHARNAME__\s*[!?]+\s*", r"\1", cleaned)
    cleaned = re.sub(r",\s*__CHARNAME__\s*,", ", ", cleaned)
    cleaned = re.sub(r",\s*__CHARNAME__([.!?])", r"\1", cleaned)
    cleaned = re.sub(r",\s*__CHARNAME__", "", cleaned)

    cleaned = cleaned.replace("__CHARNAME__", "you")
    cleaned = re.sub(r"^(?:[Yy]ou[!?]+\s+)+", "", cleaned)
    cleaned = re.sub(r"^[\s\-—]*[,.;:!?]+\s*", "", cleaned)
    cleaned = cleaned.lstrip('"')
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


# ---------------------------------------------------------------------------
# Vocalization handling
# ---------------------------------------------------------------------------
def transform_vocalization_text(text: str, voc_type: VocalizationType) -> str:
    """
    Transform vocalization text for better TTS synthesis.
    
    Converts non-phonetic spellings to more TTS-friendly versions.
    
    Args:
        text: Original vocalization text (e.g., "Gllgghh!")
        voc_type: Detected vocalization type
        
    Returns:
        Transformed text more suitable for TTS
    """
    text_lower = text.lower().strip()
    
    # Remove excessive punctuation but preserve one exclamation/period
    has_exclaim = '!' in text
    has_period = '.' in text
    text_clean = re.sub(r'[!.]{2,}', '', text_lower)
    text_clean = text_clean.rstrip('!.')
    
    # Type-specific transformations
    transformations = {
        VocalizationType.GRUNT: {
            r'^g+l+[gh]+': 'aarrgh',
            r'^u+g+h*': 'urgh',
            r'^g+r+h*': 'grrr',
            r'^u+h+': 'uhh',
        },
        VocalizationType.YELL: {
            r'^n+o+': 'nooo',
            r'^[ra]+[gh]*': 'raaagh',
            r'^a+h*': 'aaah',
        },
        VocalizationType.SCREAM: {
            r'^a+h*': 'aaaah',
            r'^e+[k]*': 'eeeek',
        },
        VocalizationType.MOAN: {
            r'^o+[hw]*': 'ohhh',
            r'^u+h+': 'uhhh',
        },
        VocalizationType.GASP: {
            r'^[ha]+[sp]*': 'hasp',
        },
        VocalizationType.LAUGH: {
            r'^he+h*': 'hehe',
            r'^ha+h*': 'haha',
        },
        VocalizationType.CRY: {
            r'^[nw]+o+': 'wooo',
        },
        VocalizationType.COUGH: {
            r'^c+o+u*g*h*': 'cough',
            r'^\*\s*cough\s*\*': 'cough',
        },
        VocalizationType.SIGH: {
            r'^[ha]+h*': 'ahhh',
            r'^\*\s*sigh\s*\*': 'sigh',
        },
    }
    
    if voc_type in transformations:
        for pattern, replacement in transformations[voc_type].items():
            if re.match(pattern, text_clean):
                text_clean = replacement
                break
    
    # Restore punctuation
    if has_exclaim:
        text_clean += '!'
    elif has_period:
        text_clean += '...'
    
    return text_clean


def get_vocalization_emotion_preset(
    speaker: str,
    voc_type: VocalizationType,
    voice_config: dict[str, object]
) -> dict[str, object] | None:
    """
    Get emotion preset for vocalization.
    
    Fallback chain:
    1. Character-specific emotion preset
    2. Character generic preset
    3. Global generic preset
    4. None (no emotion enhancement)
    
    Args:
        speaker: Character name
        voc_type: Vocalization type
        voice_config: Character's voice configuration
        
    Returns:
        Emotion configuration dict or None
    """
    # Check for emotion_presets in character config
    emotion_presets = voice_config.get("emotion_presets")
    if not emotion_presets or not isinstance(emotion_presets, dict):
        # Check global generic emotions
        global_emotions = VOICE_MAP.get("_generic_emotions_")
        if global_emotions and isinstance(global_emotions, dict):
            return global_emotions.get(voc_type.value)
        return None
    
    # Try character-specific emotion for this vocalization type
    preset = emotion_presets.get(voc_type.value)
    if preset:
        return preset
    
    # Try character generic fallback
    preset = emotion_presets.get("generic")
    if preset:
        return preset
    
    # Try global generic
    global_emotions = VOICE_MAP.get("_generic_emotions_")
    if global_emotions and isinstance(global_emotions, dict):
        return global_emotions.get(voc_type.value)
    
    return None


# ---------------------------------------------------------------------------
# Batch synthesiser
# ---------------------------------------------------------------------------
class BatchSynthesiser:
    """Keeps Index-TTS loaded in memory for rapid synthesis."""

    def __init__(self) -> None:
        if str(INDEX_TTS_ROOT) not in sys.path:
            sys.path.insert(0, str(INDEX_TTS_ROOT))

        try:
            cache_utils = importlib.import_module("transformers.cache_utils")
        except ModuleNotFoundError as exc:
            raise RuntimeError("transformers is required for Index-TTS") from exc

        if not hasattr(cache_utils, "QuantizedCacheConfig"):
            class _QuantizedCacheConfig:  # minimal stub for compatibility gaps
                pass

            cache_utils.QuantizedCacheConfig = _QuantizedCacheConfig  # type: ignore[attr-defined]

        try:
            candidate_gen = importlib.import_module("transformers.generation.candidate_generator")
        except ModuleNotFoundError:
            candidate_gen = None

        if candidate_gen and not hasattr(candidate_gen, "_crop_past_key_values"):
            def _crop_past_key_values(past_key_values, *args, **kwargs):  # type: ignore[no-untyped-def]
                return past_key_values

            candidate_gen._crop_past_key_values = _crop_past_key_values  # type: ignore[attr-defined]

        try:
            from indextts.infer_v2 import IndexTTS2 as _IndexTTS2  # type: ignore[import-not-found]
        except ModuleNotFoundError as exc:  # pragma: no cover - clearer error to caller
            raise RuntimeError(
                "Index-TTS not found. Please install the repo or update index_tts_root in config."
            ) from exc

        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"🧠 Initialising Index-TTS (device={self.device})")
        self.tts = _IndexTTS2(
            cfg_path=str(INDEX_TTS_CONFIG),
            model_dir=str(INDEX_TTS_ROOT / "checkpoints"),
            use_fp16=torch.cuda.is_available(),
            device=self.device,
        )

    def generate(self, voice_ref: str | None, text: str, out_wav: Path, config: dict) -> None:
        kwargs: dict[str, object] = {
            "text": text,
            "output_path": str(out_wav),
            "verbose": False,
            "num_beams": 1,
            "do_sample": False,
        }

        if voice_ref:
            if voice_ref.lower().endswith(".wav"):
                kwargs["spk_audio_prompt"] = voice_ref
            else:
                kwargs["voice"] = voice_ref

        # Optional parameters supported by Index-TTS
        for key in ("emo_audio_prompt", "emo_alpha", "emo_vector", "emo_text",
                    "interval_silence", "use_random", "max_text_tokens_per_segment"):
            if key in config and config[key] is not None:
                value = config[key]
                if key == "emo_audio_prompt" and isinstance(value, str):
                    emo_path = Path(value)
                    if not emo_path.is_absolute():
                        value = str((ROOT / emo_path).resolve())
                kwargs[key] = value

        if config.get("emo_text"):
            kwargs["use_emo_text"] = True

        self.tts.infer(**kwargs)


def resolve_voice_config(speaker: str) -> tuple[str | None, dict[str, object]]:
    """Return voice reference and configuration dict for a speaker."""
    config = VOICE_MAP.get(speaker, VOICE_MAP.get("_default_", {"voice": "narrator"}))

    if isinstance(config, str):
        voice_ref = config
        config_dict: dict[str, object] = {}
    elif isinstance(config, dict):
        voice_ref = config.get("ref") or config.get("voice") or "narrator"
        config_dict = {k: v for k, v in config.items() if k not in {"ref", "voice", "notes", "status"}}
    else:
        voice_ref = "narrator"
        config_dict = {}

    if voice_ref and voice_ref.lower().endswith(".wav"):
        ref_path = Path(voice_ref)
        if not ref_path.is_absolute():
            voice_ref = str((ROOT / ref_path).resolve())

    return voice_ref, config_dict


def apply_post_processing(out_wav: Path, speed: float | None, pitch_shift: float | None) -> None:
    if not speed and not pitch_shift:
        return

    sample_rate, audio = wavfile.read(str(out_wav))
    if audio.dtype != np.int16:
        audio = (audio * 32767).astype(np.int16)

    if speed and speed != 1.0:
        audio, sample_rate = change_speed(audio, sample_rate, speed)
    if pitch_shift and pitch_shift != 0:
        audio = change_pitch(audio, sample_rate, pitch_shift)

    wavfile.write(str(out_wav), sample_rate, audio)


def synth_batch(csv_path: Path) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {csv_path}")

    print(f"📄 Reading lines from: {csv_path}")
    with open(csv_path, newline="", encoding="utf-8") as lines_file:
        rows = list(csv.DictReader(lines_file))

    total = len(rows)
    print(f"   Total entries: {total}")

    synthesiser = BatchSynthesiser()
    start_time = time.perf_counter()
    generated = 0
    skipped = 0

    for idx, row in enumerate(rows, start=1):
        strref = row.get("StrRef", "").strip()
        speaker = row.get("Speaker", "").strip()
        text = row.get("Text", "")
        manual_emotion = row.get("Emotion")
        original_vo = row.get("Original_VO_WAV", "").strip()

        if not strref or not speaker or not text:
            skipped += 1
            continue

        # Skip lines that already have professional voice acting
        if original_vo:
            skipped += 1
            continue

        out_wav = OUT / f"{strref}.wav"
        if out_wav.exists():
            skipped += 1
            continue

        sanitized = sanitize(text)
        if not sanitized:
            skipped += 1
            continue

        voice_ref, config_dict = resolve_voice_config(speaker)

        # Check if text is a vocalization (NEW)
        voc_result = classify_text(sanitized, min_confidence=0.6)
        is_vocalization = voc_result is not None
        
        # Emotion handling
        emotion_config = None
        emotion_label = None
        
        # Priority 1: Vocalization emotion presets (NEW)
        if is_vocalization and voc_result:
            voc_type = voc_result['type']
            voc_confidence = voc_result['confidence']
            
            # Get emotion preset for this vocalization
            voc_emotion = get_vocalization_emotion_preset(speaker, voc_type, config_dict)
            
            if voc_emotion:
                emotion_config = voc_emotion.copy()
                emotion_label = f"{voc_type.value} ({voc_confidence:.2f})"
                
                # Transform text for better TTS (if pure vocalization)
                if voc_result.get('is_pure'):
                    transformed = transform_vocalization_text(sanitized, voc_type)
                    if transformed != sanitized:
                        print(f"   📝 Transform: '{sanitized}' -> '{transformed}'")
                        sanitized = transformed
        
        # Priority 2: Manual emotion from CSV
        if not emotion_config and manual_emotion and manual_emotion.strip():
            emotion_label = manual_emotion.strip().lower()
            emotion_config = get_emotion_config(emotion_label, speaker)
        
        # Priority 3: Auto-detect emotion (Ilyich special case)
        if not emotion_config and speaker.lower() == "ilyich":
            emotion_label = detect_emotion(sanitized)
            emotion_config = get_emotion_config(emotion_label, speaker)

        if emotion_config:
            if "emo_audio_prompt" in emotion_config:
                emo_path = Path(emotion_config["emo_audio_prompt"])
                if not emo_path.is_absolute():
                    emotion_config["emo_audio_prompt"] = str((ROOT / emo_path).resolve())
            config_dict.update(emotion_config)

        pitch_shift = config_dict.pop("pitch_shift", None)
        speed_adjust = config_dict.pop("speed", None)

        try:
            print(f"[{idx}/{total}] {speaker} -> {strref}")
            if emotion_label:
                print(f"   🎭 Emotion: {emotion_label}")
            synthesiser.generate(voice_ref, sanitized, out_wav, config_dict)
            apply_post_processing(out_wav, speed_adjust, pitch_shift)
            generated += 1
        except Exception as exc:  # pragma: no cover - log and continue
            print(f"   ⚠️ Failed to generate {strref}: {exc}")
            if out_wav.exists():
                out_wav.unlink(missing_ok=True)

    elapsed = time.perf_counter() - start_time
    rtf = elapsed / max(generated, 1)

    print("\n✅ Batch synthesis complete")
    print(f"   Generated: {generated}")
    print(f"   Skipped:   {skipped}")
    print(f"   Elapsed:   {elapsed/60:.2f} minutes")
    print(f"   Avg time per line: {rtf:.2f} seconds")

    return generated  # Return count for caller


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch Index-TTS synthesis that keeps models in memory")
    parser.add_argument("--input", type=Path, default=None, help="Input CSV (default: data/chapter1_unvoiced_only.csv)")
    parser.add_argument("--auto-update", action="store_true", default=True, help="Auto-update project stats after synthesis (default: True)")
    parser.add_argument("--no-auto-update", action="store_false", dest="auto_update", help="Disable auto-update of project stats")
    args = parser.parse_args()

    input_csv = args.input
    if input_csv is None:
        input_csv = ROOT / "data" / "chapter1_unvoiced_only.csv"

    generated = synth_batch(input_csv)

    # Auto-update statistics after successful synthesis
    if args.auto_update and generated > 0:
        print("\n📊 Updating project statistics...")
        try:
            update_stats()
            print("   ✅ Statistics updated successfully")
        except Exception as exc:
            print(f"   ⚠️ Failed to update statistics: {exc}")
            print("   💡 Run 'python scripts/utils/update_project_stats.py' manually if needed")


if __name__ == "__main__":
    main()
