"""Cho phép các file test import trực tiếp các module trong backend/."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
