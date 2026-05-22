#!/usr/bin/env python3
"""U8: Export HeyReach import CSV (LinkedIn-only, no email/phone)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tam_builder.josh_pilot.export_campaigns import main

if __name__ == "__main__":
    raise SystemExit(main())
