#!/usr/bin/env python3
"""U4: Merge Josh candidates with wave1/ACO fixtures."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tam_builder.josh_pilot.merge_fixtures import main

if __name__ == "__main__":
    raise SystemExit(main())
