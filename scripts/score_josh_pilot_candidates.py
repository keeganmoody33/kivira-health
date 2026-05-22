#!/usr/bin/env python3
"""U5: Score and select per-subtier finalists."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tam_builder.josh_pilot.score import main

if __name__ == "__main__":
    raise SystemExit(main())
