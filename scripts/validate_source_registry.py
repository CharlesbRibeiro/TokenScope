"""Validate Source Registry documents and optionally generate their schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from tokenscope_dd import config
from tokenscope_dd.source_registry import (
    SourceRegistryLoadError,
    ValidationStatus,
    load_complete_source_context,
    validate_complete_source_context,
    write_source_registry_schema,
)


DEFAULT_TAXONOMY = config.CONFIGS_DIR / "taxonomy" / "source_taxonomy.yaml"
DEFAULT_CANDIDATES = (
    config.CONFIGS_DIR / "registries" / "source_candidates.yaml"
)
DEFAULT_SOURCES = config.CONFIGS_DIR / "registries" / "sources.yaml"
DEFAULT_INVESTIGATION = (
    config.CONFIGS_DIR / "registries" / "source_investigation.yaml"
)
DEFAULT_ASSET_REGISTRY = config.CONFIGS_DIR / "registries" / "assets.yaml"
DEFAULT_ASSET_CANDIDATES = (
    config.CONFIGS_DIR / "registries" / "asset_candidates.yaml"
)
DEFAULT_SCHEMA = config.REPOSITORY_ROOT / "schemas" / "source_registry.schema.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate TokenScope DD Source Registry documents."
    )
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY)
    parser.add_argument(
        "--investigation",
        type=Path,
        default=DEFAULT_INVESTIGATION,
    )
    parser.add_argument(
        "--asset-registry",
        type=Path,
        default=DEFAULT_ASSET_REGISTRY,
    )
    parser.add_argument(
        "--asset-candidates",
        type=Path,
        default=DEFAULT_ASSET_CANDIDATES,
    )
    parser.add_argument(
        "--write-schema",
        action="store_true",
        help="Regenerate schemas/source_registry.schema.json from Pydantic.",
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
    source_types = ", ".join(metrics["source_types_used"]) or "(none)"
    authority_levels = (
        ", ".join(metrics["authority_levels_used"]) or "(none)"
    )
    lines = (
        ("Registry version", metrics["registry_version"]),
        ("Candidate registry version", metrics["candidate_registry_version"]),
        ("Candidates", metrics["candidate_count"]),
        ("Official sources", metrics["source_count"]),
        ("Verified sources", metrics["verified_sources"]),
        ("Collection-ready sources", metrics["ready_sources"]),
        ("Blocked sources", metrics["blocked_sources"]),
        ("Endpoints", metrics["endpoint_count"]),
        ("Investigation items", metrics["investigation_count"]),
        ("Source types used", source_types),
        ("Authority levels used", authority_levels),
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
    args = build_parser().parse_args(argv)
    if args.write_schema:
        schema_path = write_source_registry_schema(DEFAULT_SCHEMA)
        print(f"Schema written: {schema_path}")

    try:
        context = load_complete_source_context(
            taxonomy_path=args.taxonomy,
            candidates_path=args.candidates,
            sources_path=args.sources,
            investigation_path=args.investigation,
            asset_registry_path=args.asset_registry,
            asset_candidates_path=args.asset_candidates,
        )
    except SourceRegistryLoadError as exc:
        print("Final status: FAILED")
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

    result = validate_complete_source_context(context)
    _print_result(result)
    if args.json_output:
        _write_json_report(args.json_output, result.model_dump(mode="json"))
        print(f"JSON report written: {args.json_output}")
    return 1 if result.status is ValidationStatus.FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
