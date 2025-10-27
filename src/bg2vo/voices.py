"""Voice preset helpers."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable


@dataclass
class VoicePreset:
    name: str
    voice: str | None = None
    speed: float | None = None
    pitch: float | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload = dict(self.metadata)
        if self.voice is not None:
            payload["voice"] = self.voice
        if self.speed is not None:
            payload["speed"] = self.speed
        if self.pitch is not None:
            payload["pitch"] = self.pitch
        return payload


def _normalize_payload(payload: Any) -> Dict[str, Any]:
    if isinstance(payload, str):
        return {"voice": payload}
    if isinstance(payload, dict):
        return dict(payload)
    raise ValueError(f"Unsupported voice preset payload type: {type(payload)!r}")


def _to_float(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def load_presets(path: Path) -> Dict[str, VoicePreset]:
    data = json.loads(path.read_text(encoding="utf-8"))
    presets: Dict[str, VoicePreset] = {}
    for name, payload in data.items():
        normalized = _normalize_payload(payload)
        voice = normalized.pop("voice", None)
        speed = _to_float(normalized.pop("speed", None))
        pitch = _to_float(normalized.pop("pitch", None))
        presets[name] = VoicePreset(
            name=name,
            voice=voice,
            speed=speed,
            pitch=pitch,
            metadata=normalized,
        )
    return presets


def voice_names(presets: Dict[str, VoicePreset]) -> Iterable[str]:
    return presets.keys()


def load_voices(path: Path) -> Dict[str, VoicePreset]:
    return load_presets(path)
