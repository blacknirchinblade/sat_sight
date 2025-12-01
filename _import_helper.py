"""
Import helper to make the package work both as installed and from source.
Add this at the top of any script that imports from sat_sight:

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
"""

import sys
from pathlib import Path

def setup_path():
    """Add parent directory to path if not already there."""
    parent = str(Path(__file__).parent.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
