#!/usr/bin/env python3
"""U7: LinkedIn profile quality gate for HeyReach export."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tam_builder.josh_pilot.gate import main

if __name__ == "__main__":
    raise SystemExit(main())
