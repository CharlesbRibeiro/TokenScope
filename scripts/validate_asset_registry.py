"""Validate the TokenScope DD Asset Registry and optionally write its schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from tokenscope_dd import config
from tokenscope_dd.registry import (
    RegistryLoadError,
    ValidationStatus,
    load_complete_registry_context,
    validate_complete_registry,
    write_asset_registry_schema,
)


DEFAULT_TAXONOMY = config.CONFIGS_DIR / "taxonomy" / "asset_categories.yaml"
DEFAULT_CANDIDATES = config.CONFIGS_DIR / "registries" / "asset_candidates.yaml"
DEFAULT_ASSETS = config.CONFIGS_DIR / "registries" / "assets.yaml"
DEFAULT_INVESTIGATION = (
    config.CONFIGS_DIR / "registries" / "entity_investigation.yaml"
)
DEFAULT_SCHEMA = config.REPOSITORY_ROOT / "schemas" / "asset_registry.schema.json"


def build_parser() -> argparse.ArgumentParser:
    """Build the small command-line interface used locally and by tests."""

    parser = argparse.ArgumentParser(
        description="Validate TokenScope DD Asset Registry documents."
    )
    parser.add_argument("--assets", type=Path, default=DEFAULT_ASSETS)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY)
    parser.add_argument(
        "--investigation",
        type=Path,
        default=DEFAULT_INVESTIGATION,
    )
    parser.add_argument(
        "--write-schema",
        action="store_true",
        help="Regenerate schemas/asset_registry.schema.json from Pydantic.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Write the validation result as UTF-8 JSON.",
    )
    return parser


def _print_result(result: object) -> None:
    payload = result.model_dump(mode="json")
    metrics = payload["metrics"]
    categories = ", ".join(metrics["categories_used"]) or "(none)"
    lines = (
        ("Registry version", metrics["registry_version"]),
        ("Candidate registry version", metrics["candidate_registry_version"]),
        ("Candidates", metrics["candidate_count"]),
        ("Official assets", metrics["asset_count"]),
        ("Verified assets", metrics["verified_assets"]),
        ("Unverified assets", metrics["unverified_assets"]),
        ("Analysis-ready assets", metrics["analysis_ready_assets"]),
        ("Pending investigations", metrics["pending_investigations"]),
        ("Categories used", categories),
        ("Duplicates found", metrics["duplicate_count"]),
        ("Errors", metrics["error_count"]),
        ("Warnings", metrics["warning_count"]),
        ("Registry fingerprint", payload["registry_fingerprint"]),
        ("Final status", payload["status"]),
    )
    for label, value in lines:
        print(f"{label}: {value}")
    for error in payload["errors"]:
        print(f"ERROR: {error}")
    for warning in payload["warnings"]:
        print(f"WARNING: {warning}")


def _write_json_report(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main(argv: Sequence[str] | None = None) -> int:
    """Run validation and return a process-compatible status code."""

    args = build_parser().parse_args(argv)
    if args.write_schema:
        schema_path = write_asset_registry_schema(DEFAULT_SCHEMA)
        print(f"Schema written: {schema_path}")

    try:
        context = load_complete_registry_context(
            taxonomy_path=args.taxonomy,
            candidates_path=args.candidates,
            assets_path=args.assets,
            investigation_path=args.investigation,
        )
    except RegistryLoadError as exc:
        print(f"Final status: FAILED")
        print(f"ERROR: {exc}")
        if args.json_output:
            _write_json_report(
                args.json_output,
                {
                    "status": ValidationStatus.FAILED.value,
                    "errors": [str(exc)],
                    "warnings": [],
                    "metrics": {},
                    "registry_fingerprint": None,
                },
            )
        return 1

    result = validate_complete_registry(context)
    _print_result(result)
    if args.json_output:
        _write_json_report(args.json_output, result.model_dump(mode="json"))
        print(f"JSON report written: {args.json_output}")
    return 1 if result.status is ValidationStatus.FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
