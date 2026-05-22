#!/usr/bin/env python3
"""U2: Pre-filter Josh exec export. See tam_builder.josh_pilot.filter_candidates."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tam_builder.josh_pilot.filter_candidates import main

if __name__ == "__main__":
    raise SystemExit(main())
