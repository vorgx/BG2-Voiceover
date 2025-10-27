"""Lightweight audit helpers to sanity-check generated datasets."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Iterable

from .lines import LineRecord, read_lines


def speaker_counts(lines: Iterable[LineRecord]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for line in lines:
        counts[line.speaker] += 1
    return counts


def report_csv(path: Path) -> Counter[str]:
    return speaker_counts(read_lines(path))


def count_lines(path: Path) -> Counter[str]:
    return report_csv(path)
