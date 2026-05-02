"""Command line interface for the Kivira TAM builder."""

from __future__ import annotations

import argparse
from pathlib import Path

from tam_builder.adapters import get_adapter
from tam_builder.briefing import generate_briefs
from tam_builder.constants import (
    BRIEF_FIELDS,
    ERROR_FIELDS,
    ESTIMATE_FIELDS,
    NORMALIZED_ACCOUNT_FIELDS,
    ROUTED_FIELDS,
    TIER_FIELDS,
)
from tam_builder.estimation import estimate_accounts
from tam_builder.io_utils import ensure_directory, read_csv, write_csv
from tam_builder.normalize import normalize_accounts
from tam_builder.personas import route_persona_row
from tam_builder.tiering import tier_account_row


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Kivira TAM builder with CoCM wedge.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    normalize_parser = subparsers.add_parser("normalize-accounts", help="Normalize raw account CSVs.")
    normalize_parser.add_argument("--input", required=True)
    normalize_parser.add_argument("--output", required=True)
    normalize_parser.add_argument("--errors-output")
    normalize_parser.add_argument("--mapping-file")
    normalize_parser.set_defaults(func=cmd_normalize_accounts)

    estimate_parser = subparsers.add_parser("estimate-cocm", help="Estimate CoCM opportunity from normalized accounts.")
    estimate_parser.add_argument("--input", required=True)
    estimate_parser.add_argument("--output", required=True)
    estimate_parser.add_argument("--artifact-dir", required=True)
    estimate_parser.add_argument("--adapter", default="synthetic", choices=["synthetic", "live-public"])
    estimate_parser.add_argument("--include-low-confidence", action="store_true")
    estimate_parser.set_defaults(func=cmd_estimate_cocm)

    tier_parser = subparsers.add_parser("tier-accounts", help="Assign outreach tiers.")
    tier_parser.add_argument("--input", required=True)
    tier_parser.add_argument("--output", required=True)
    tier_parser.set_defaults(func=cmd_tier_accounts)

    route_parser = subparsers.add_parser("route-personas", help="Map accounts to persona sequences and titles.")
    route_parser.add_argument("--input", required=True)
    route_parser.add_argument("--output", required=True)
    route_parser.set_defaults(func=cmd_route_personas)

    brief_parser = subparsers.add_parser("generate-briefs", help="Generate discovery-safe briefs by persona.")
    brief_parser.add_argument("--input", required=True)
    brief_parser.add_argument("--output", required=True)
    brief_parser.set_defaults(func=cmd_generate_briefs)

    return parser


def cmd_normalize_accounts(args: argparse.Namespace) -> int:
    rows = read_csv(args.input)
    normalized_rows, errors, _ = normalize_accounts(rows, mapping_file=args.mapping_file)
    write_csv(args.output, normalized_rows, NORMALIZED_ACCOUNT_FIELDS)
    errors_output = args.errors_output or str(Path(args.output).with_suffix(".errors.csv"))
    write_csv(errors_output, errors, ERROR_FIELDS)
    return 1 if errors else 0


def cmd_estimate_cocm(args: argparse.Namespace) -> int:
    rows = read_csv(args.input)
    adapter = get_adapter(args.adapter)
    estimates = estimate_accounts(
        rows,
        adapter=adapter,
        artifact_dir=args.artifact_dir,
        include_low_confidence=args.include_low_confidence,
    )
    write_csv(args.output, estimates, ESTIMATE_FIELDS)
    return 0


def cmd_tier_accounts(args: argparse.Namespace) -> int:
    rows = read_csv(args.input)
    tiered = [tier_account_row(row) for row in rows]
    write_csv(args.output, tiered, TIER_FIELDS)
    return 0


def cmd_route_personas(args: argparse.Namespace) -> int:
    rows = read_csv(args.input)
    routed = [route_persona_row(row) for row in rows]
    write_csv(args.output, routed, ROUTED_FIELDS)
    return 0


def cmd_generate_briefs(args: argparse.Namespace) -> int:
    rows = read_csv(args.input)
    briefs = generate_briefs(rows)
    write_csv(args.output, briefs, BRIEF_FIELDS)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "estimate-cocm":
        ensure_directory(args.artifact_dir)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
