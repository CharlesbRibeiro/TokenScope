"""Canonical JSON and SHA-256 fingerprints for the Source Registry."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel

from tokenscope_dd.source_registry.models import (
    CompleteSourceRegistryContext,
    SourceCandidateRegistry,
    SourceInvestigationRegistry,
    SourceRegistry,
)
from tokenscope_dd.source_registry.normalization import normalize_identity_text


def _drop_fingerprint_fields(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: _drop_fingerprint_fields(item)
            for key, item in value.items()
            if key not in {"fingerprint", "registry_fingerprint"}
        }
    if isinstance(value, list):
        return [_drop_fingerprint_fields(item) for item in value]
    return value


def _sort_endpoint_payload(endpoint: dict[str, Any]) -> dict[str, Any]:
    return dict(endpoint)


def _sort_source_payload(source: dict[str, Any]) -> dict[str, Any]:
    result = dict(source)
    result["endpoints"] = sorted(
        (
            _sort_endpoint_payload(endpoint)
            for endpoint in result.get("endpoints", [])
        ),
        key=lambda endpoint: endpoint["endpoint_id"],
    )
    for field in (
        "information_domains",
        "related_asset_ids",
        "verification_refs",
    ):
        result[field] = sorted(
            result.get(field, []),
            key=lambda value: (normalize_identity_text(value), value),
        )
    return result


def _sort_candidate_payload(candidate: dict[str, Any]) -> dict[str, Any]:
    result = dict(candidate)
    result["related_asset_candidate_ids"] = sorted(
        result.get("related_asset_candidate_ids", [])
    )
    return result


def _canonicalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    result = _drop_fingerprint_fields(payload)
    if "sources" in result and isinstance(result["sources"], list):
        result["sources"] = sorted(
            (_sort_source_payload(source) for source in result["sources"]),
            key=lambda source: source["source_id"],
        )
    if "candidates" in result and isinstance(result["candidates"], list):
        result["candidates"] = sorted(
            (
                _sort_candidate_payload(candidate)
                for candidate in result["candidates"]
            ),
            key=lambda candidate: candidate["candidate_id"],
        )
    if "items" in result and isinstance(result["items"], list):
        for item in result["items"]:
            item["related_candidate_ids"] = sorted(
                item.get("related_candidate_ids", [])
            )
        result["items"] = sorted(
            result["items"],
            key=lambda item: item["investigation_id"],
        )
    for field in (
        "source_types",
        "authority_levels",
        "officiality_statuses",
        "information_domains",
        "access_methods",
    ):
        if field in result and isinstance(result[field], list):
            result[field] = sorted(result[field])
    return result


def canonical_registry_payload(
    registry: BaseModel | Mapping[str, Any],
) -> dict[str, Any]:
    """Return a deterministic representation of one source document."""

    if isinstance(registry, BaseModel):
        payload = registry.model_dump(mode="json")
    else:
        payload = dict(registry)
    return _canonicalize_payload(payload)


def canonical_registry_json(
    registry: BaseModel | Mapping[str, Any],
) -> str:
    return json.dumps(
        canonical_registry_payload(registry),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def calculate_registry_fingerprint(
    registry: BaseModel | Mapping[str, Any],
) -> str:
    canonical = canonical_registry_json(registry)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def canonical_context_payload(
    context: CompleteSourceRegistryContext,
) -> dict[str, Any]:
    """Canonicalize source documents plus referenced Asset Registry identity."""

    return {
        "taxonomy": canonical_registry_payload(context.taxonomy),
        "candidates": canonical_registry_payload(context.candidates),
        "sources": canonical_registry_payload(context.sources),
        "investigation": canonical_registry_payload(context.investigation),
        "asset_registry": canonical_registry_payload(context.asset_registry),
        "asset_candidates": canonical_registry_payload(
            context.asset_candidates
        ),
    }


def calculate_context_fingerprint(
    context: CompleteSourceRegistryContext,
) -> str:
    return calculate_registry_fingerprint(canonical_context_payload(context))


def registry_versions(
    sources: SourceRegistry,
    candidates: SourceCandidateRegistry,
    investigation: SourceInvestigationRegistry,
) -> dict[str, str]:
    return {
        "registry_version": sources.registry_version,
        "candidate_registry_version": candidates.candidate_registry_version,
        "investigation_registry_version": (
            investigation.investigation_registry_version
        ),
    }
