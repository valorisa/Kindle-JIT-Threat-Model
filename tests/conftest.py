"""
conftest.py

Permet aux tests d'importer les scripts de src/detector/ directement,
sans nécessiter la création d'un package Python installable.
"""

import sys
from pathlib import Path

DETECTOR_DIR = Path(__file__).parent.parent / "src" / "detector"
sys.path.insert(0, str(DETECTOR_DIR))
