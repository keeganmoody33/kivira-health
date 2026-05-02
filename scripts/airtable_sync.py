#!/usr/bin/env python3
"""Sync TAM builder outputs to Airtable (system-of-record).

This script is intentionally minimal and safe:
- It never deletes records.
- It upserts based on a key field (default: normalized_org_key).
- It requires an Airtable Personal Access Token via env var.

Env vars:
- AIRTABLE_API_TOKEN (required)

Args:
- --base-id (required)
- --table (required)
- --input (required): CSV to sync (e.g., briefs.csv or routed.csv)
- --key-field: field used for upsert matching (default: normalized_org_key)

Notes:
- Airtable field names must exist in the target table. This script will only send columns present in the CSV.
- For early Phase 1, you can sync briefs into a single table; later you can split Accounts/Contacts/Pipeline.
"""

from __future__ import annotations

import argparse
import csv
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


AIRTABLE_API_ROOT = "https://api.airtable.com/v0"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [dict((k or "").strip(), (v or "").strip()) for k, v in reader]


def _http_json(method: str, url: str, token: str, body: bytes | None = None) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "kivira-airtable-sync/1.0",
    }
    req = Request(url, data=body, method=method, headers=headers)
    with urlopen(req, timeout=60) as resp:
        data = resp.read()
        # Airtable responses are JSON; decode defensively.
        import json

        return json.loads(data.decode("utf-8"))


def _chunk(items: list[Any], size: int) -> list[list[Any]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def airtable_list_records(token: str, base_id: str, table: str, fields: list[str]) -> list[dict[str, Any]]:
    """Fetch records and only requested fields (paginated)."""
    import urllib.parse

    records: list[dict[str, Any]] = []
    offset = None
    while True:
        params: list[tuple[str, str]] = []
        for field in fields:
            params.append(("fields[]", field))
        if offset:
            params.append(("offset", offset))
        query = urllib.parse.urlencode(params)
        url = f"{AIRTABLE_API_ROOT}/{base_id}/{urllib.parse.quote(table)}?{query}"
        resp = _http_json("GET", url, token)
        records.extend(resp.get("records", []))
        offset = resp.get("offset")
        if not offset:
            break
        time.sleep(0.2)
    return records


def airtable_upsert_records(
    token: str,
    base_id: str,
    table: str,
    key_field: str,
    rows: list[dict[str, str]],
) -> None:
    import json
    import urllib.parse

    # Build an index of existing records by key_field.
    existing = airtable_list_records(token, base_id, table, fields=[key_field])
    existing_by_key: dict[str, str] = {}
    for rec in existing:
        fields = rec.get("fields", {})
        key = str(fields.get(key_field, "")).strip()
        if key:
            existing_by_key[key] = rec["id"]

    to_create: list[dict[str, Any]] = []
    to_update: list[dict[str, Any]] = []

    for row in rows:
        key = (row.get(key_field) or "").strip()
        if not key:
            continue
        fields: dict[str, Any] = {k: v for k, v in row.items() if v != ""}
        if key in existing_by_key:
            to_update.append({"id": existing_by_key[key], "fields": fields})
        else:
            to_create.append({"fields": fields})

    url = f"{AIRTABLE_API_ROOT}/{base_id}/{urllib.parse.quote(table)}"

    # Airtable supports batch operations; keep batches small.
    for batch in _chunk(to_create, 10):
        payload = json.dumps({"records": batch, "typecast": True}).encode("utf-8")
        _http_json("POST", url, token, body=payload)
        time.sleep(0.25)

    for batch in _chunk(to_update, 10):
        payload = json.dumps({"records": batch, "typecast": True}).encode("utf-8")
        _http_json("PATCH", url, token, body=payload)
        time.sleep(0.25)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Upsert a CSV into Airtable.")
    p.add_argument("--base-id", required=True)
    p.add_argument("--table", required=True)
    p.add_argument("--input", required=True)
    p.add_argument("--key-field", default="normalized_org_key")
    args = p.parse_args(argv)

    token = os.environ.get("AIRTABLE_API_TOKEN", "").strip()
    if not token:
        raise SystemExit("AIRTABLE_API_TOKEN env var is required")

    rows = read_csv(Path(args.input))
    airtable_upsert_records(token, args.base_id, args.table, args.key_field, rows)
    print(f"Synced {len(rows)} rows into Airtable base={args.base_id} table={args.table}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

