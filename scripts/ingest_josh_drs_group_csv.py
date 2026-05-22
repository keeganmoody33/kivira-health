#!/usr/bin/env python3
"""U1: Normalize Josh Drs Group CSVs. See tam_builder.josh_pilot.ingest."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tam_builder.josh_pilot.ingest import main

if __name__ == "__main__":
    raise SystemExit(main())
