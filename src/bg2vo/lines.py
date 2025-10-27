"""Line helpers and constants for the BG2 Voiceover datasets."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, List, Sequence


@dataclass
class LineRecord:
    speaker: str
    text: str
    line_id: str | None = None


def read_lines(path: Path) -> Iterator[LineRecord]:
    import csv

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            normalized = {str(key).strip().lower(): value or "" for key, value in row.items()}
            speaker = (
                normalized.get("speaker")
                or normalized.get("actor")
                or normalized.get("character")
                or ""
            )
            text = normalized.get("text") or normalized.get("line") or ""
            line_id = (
                normalized.get("line_id")
                or normalized.get("strref")
                or normalized.get("id")
            )

            yield LineRecord(
                speaker=speaker,
                text=text,
                line_id=line_id,
            )


def load_lines(path: Path) -> List[LineRecord]:
    return list(read_lines(path))


def filter_lines(
    lines: Iterable[LineRecord], *, speakers: Sequence[str] | None = None
) -> Iterator[LineRecord]:
    speakers_set = {speaker.lower() for speaker in speakers or []}
    for line in lines:
        if speakers_set and line.speaker.lower() not in speakers_set:
            continue
        yield line
