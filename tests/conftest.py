"""conftest.py — shared fixtures for DupeClean tests."""

import sys
from pathlib import Path

# Ensure src is on path for imports
src = Path(__file__).parent.parent / "src"
if str(src) not in sys.path:
    sys.path.insert(0, str(src))
