from __future__ import annotations

import json
import types
from pathlib import Path

import pytest

import bg2vo.audit as audit_mod  # type: ignore[import-not-found]
import bg2vo.config as config_mod  # type: ignore[import-not-found]
import bg2vo.lines as lines_mod  # type: ignore[import-not-found]
import bg2vo.voices as voices_mod  # type: ignore[import-not-found]

ROOT = Path(__file__).resolve().parents[1]


def test_load_config_with_json_payload(tmp_path, monkeypatch):
    cfg_path = tmp_path / "defaults.yaml"
    cfg_payload = {
        "paths": {"repo_root": str(ROOT)},
        "inputs": {"lines_csv": "data/lines.csv"},
        "outputs": {"reports_dir": "reports"},
        "index_tts": {},
        "sanitization": {},
        "synthesis": {},
        "weidu": {},
    }
    cfg_path.write_text(json.dumps(cfg_payload), encoding="utf-8")

    fake_yaml = types.SimpleNamespace(safe_load=json.loads)
    monkeypatch.setattr(config_mod, "yaml", fake_yaml)

    settings = config_mod.load_config(cfg_path)

    assert settings.paths["repo_root"] == str(ROOT)
    assert settings.inputs["lines_csv"] == "data/lines.csv"
    assert settings.outputs["reports_dir"] == "reports"


def test_load_lines_normalizes_headers(tmp_path, monkeypatch):
    csv_path = tmp_path / "lines.csv"
    csv_path.write_text("StrRef,Speaker,Text\n1,Imoen,Hello there\n2,MINSC,For Boo!\n", encoding="utf-8")

    lines = lines_mod.load_lines(csv_path)

    assert len(lines) == 2
    assert lines[0].line_id == "1"
    assert lines[0].speaker == "Imoen"
    assert lines[0].text == "Hello there"
    assert lines[1].speaker == "MINSC"  # Preserves original case
    assert lines[1].text == "For Boo!"


def test_load_voices_preserves_metadata(tmp_path):
    json_path = tmp_path / "voices.json"
    json_path.write_text(
        json.dumps(
            {
                "_default_": "narrator",
                "Jaheira": {
                    "voice": "female_determined",
                    "speed": -0.03,
                    "pitch": -0.05,
                    "notes": "Stoic ranger cadence",
                },
            }
        ),
        encoding="utf-8",
    )

    presets = voices_mod.load_voices(json_path)

    assert presets["_default_"].voice == "narrator"
    assert presets["Jaheira"].voice == "female_determined"
    assert presets["Jaheira"].speed == pytest.approx(-0.03)
    assert presets["Jaheira"].metadata["notes"] == "Stoic ranger cadence"


def test_count_lines_from_csv(tmp_path):
    csv_path = tmp_path / "lines.csv"
    csv_path.write_text("line_id,speaker,text\n1,Imoen,Hello\n2,Imoen,Go on\n3,Minsc,For Boo!\n", encoding="utf-8")

    counts = audit_mod.count_lines(csv_path)

    assert counts["Imoen"] == 2
    assert counts["Minsc"] == 1