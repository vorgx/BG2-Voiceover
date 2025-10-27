from __future__ import annotations

import json
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - provide lightweight stub for tests
    yaml_stub = types.ModuleType("yaml")
    yaml_stub.safe_load = json.loads  # type: ignore[attr-defined]
    sys.modules.setdefault("yaml", yaml_stub)
