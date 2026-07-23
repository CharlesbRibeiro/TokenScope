"""Deterministic canonicalization and SHA-256 fingerprints for registries."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel

from tokenscope_dd.registry.models import (
    AssetRegistry,
    CandidateRegistry,
    CompleteRegistryContext,
    EntityInvestigationRegistry,
)


def normalize_identity_text(value: str) -> str:
    """Normalize identity text for deterministic comparisons without mutation."""

    decomposed = unicodedata.normalize("NFKD", value.casefold().strip())
    without_marks = "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )
    simple_punctuation = re.sub(r"[\W_]+", " ", without_marks, flags=re.UNICODE)
    return " ".join(simple_punctuation.split())


def generate_candidate_id(
    observed_name: str,
    observed_symbol: str | None,
    discovered_in: str,
) -> str:
    """Generate a stable candidate ID from the original normalized observation."""

    identity = "|".join(
        (
            normalize_identity_text(discovered_in),
            normalize_identity_text(observed_name),
            normalize_identity_text(observed_symbol or ""),
        )
    )
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]
    return f"ts_candidate_{digest}"


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


def _sort_asset_payload(asset: dict[str, Any]) -> dict[str, Any]:
    result = dict(asset)
    result["aliases"] = sorted(
        result.get("aliases", []),
        key=lambda alias: (normalize_identity_text(alias), alias),
    )
    for field in ("jurisdictions", "source_refs"):
        result[field] = sorted(result.get(field, []), key=normalize_identity_text)
    result["network_deployments"] = sorted(
        result.get("network_deployments", []),
        key=lambda deployment: (
            normalize_identity_text(deployment["network_name"]),
            deployment.get("chain_id") or "",
            (deployment.get("contract_address") or "").casefold(),
            normalize_identity_text(deployment.get("token_standard") or ""),
            deployment["deployment_status"],
        ),
    )
    return result


def _canonicalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    result = _drop_fingerprint_fields(payload)
    if "assets" in result and isinstance(result["assets"], list):
        result["assets"] = sorted(
            (_sort_asset_payload(asset) for asset in result["assets"]),
            key=lambda asset: asset["asset_id"],
        )
    if "candidates" in result and isinstance(result["candidates"], list):
        result["candidates"] = sorted(
            result["candidates"],
            key=lambda candidate: candidate["candidate_id"],
        )
    if "categories" in result and isinstance(result["categories"], list):
        result["categories"] = sorted(
            result["categories"],
            key=lambda category: category["category_id"],
        )
    if "entities" in result and isinstance(result["entities"], list):
        result["entities"] = sorted(
            result["entities"],
            key=lambda entity: normalize_identity_text(entity["observed_name"]),
        )
    return result


def canonical_registry_payload(
    registry: BaseModel | Mapping[str, Any],
) -> dict[str, Any]:
    """Return an order-stable representation of one registry document."""

    if isinstance(registry, BaseModel):
        payload = registry.model_dump(mode="json")
    else:
        payload = dict(registry)
    return _canonicalize_payload(payload)


def canonical_registry_json(
    registry: BaseModel | Mapping[str, Any],
) -> str:
    """Serialize a registry with stable ordering and UTF-8-compatible JSON."""

    return json.dumps(
        canonical_registry_payload(registry),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def calculate_registry_fingerprint(
    registry: BaseModel | Mapping[str, Any],
) -> str:
    """Calculate a deterministic SHA-256 fingerprint."""

    canonical = canonical_registry_json(registry)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def canonical_context_payload(context: CompleteRegistryContext) -> dict[str, Any]:
    """Canonicalize all registry documents for a complete-context fingerprint."""

    return {
        "taxonomy": canonical_registry_payload(context.taxonomy),
        "candidates": canonical_registry_payload(context.candidates),
        "assets": canonical_registry_payload(context.assets),
        "investigation": canonical_registry_payload(context.investigation),
    }


def calculate_context_fingerprint(context: CompleteRegistryContext) -> str:
    """Calculate a deterministic fingerprint for the complete registry context."""

    return calculate_registry_fingerprint(canonical_context_payload(context))


def registry_versions(
    assets: AssetRegistry,
    candidates: CandidateRegistry,
    investigation: EntityInvestigationRegistry,
) -> dict[str, str]:
    """Expose registry versions for reports without coupling them to validation."""

    return {
        "registry_version": assets.registry_version,
        "candidate_registry_version": candidates.candidate_registry_version,
        "investigation_registry_version": (
            investigation.investigation_registry_version
        ),
    }
