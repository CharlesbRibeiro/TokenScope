"""Cross-document business validation for the Source Registry."""

from __future__ import annotations

import json
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from tokenscope_dd.source_registry.fingerprint import (
    calculate_context_fingerprint,
)
from tokenscope_dd.source_registry.models import (
    AccessMethod,
    AccessStatus,
    CandidateStatus,
    CollectionReadiness,
    CompleteSourceRegistryContext,
    EndpointStatus,
    OfficialSource,
    RecordStatus,
    SourceRegistry,
    SourceType,
    VerificationStatus,
)
from tokenscope_dd.source_registry.normalization import (
    generate_endpoint_id,
    normalize_identity_text,
    normalize_locator,
    normalize_url,
)


class ValidationStatus(str, Enum):
    PASSED = "PASSED"
    PASSED_WITH_WARNINGS = "PASSED_WITH_WARNINGS"
    FAILED = "FAILED"


class SourceRegistryValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: ValidationStatus
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    registry_fingerprint: str


SUPPORTED_READY_METHODS = frozenset(
    {
        AccessMethod.HTTP_HTML,
        AccessMethod.HTTP_PDF,
        AccessMethod.HTTP_JSON,
        AccessMethod.API,
        AccessMethod.FILE,
        AccessMethod.BLOCKCHAIN_EXPLORER,
    }
)


def _endpoint_identity(endpoint: object) -> str | None:
    if endpoint.url is not None:
        return f"url:{normalize_url(endpoint.url)}"
    if endpoint.locator is not None:
        return f"locator:{normalize_locator(endpoint.locator)}"
    return None


def _validate_taxonomy(
    context: CompleteSourceRegistryContext,
    errors: list[str],
) -> None:
    taxonomy = context.taxonomy
    allowed_types = set(taxonomy.source_types)
    allowed_authorities = set(taxonomy.authority_levels)
    allowed_officiality = set(taxonomy.officiality_statuses)
    allowed_domains = set(taxonomy.information_domains)
    allowed_methods = set(taxonomy.access_methods)
    for candidate in context.candidates.candidates:
        if candidate.possible_source_type not in allowed_types:
            errors.append(
                f"Candidate {candidate.candidate_id} uses a source type "
                "absent from the taxonomy."
            )
    for source in context.sources.sources:
        if source.source_type not in allowed_types:
            errors.append(
                f"Source {source.source_id} uses a source type absent "
                "from the taxonomy."
            )
        if source.authority_level not in allowed_authorities:
            errors.append(
                f"Source {source.source_id} uses an authority level absent "
                "from the taxonomy."
            )
        if source.officiality_status not in allowed_officiality:
            errors.append(
                f"Source {source.source_id} uses an officiality status absent "
                "from the taxonomy."
            )
        missing_domains = set(source.information_domains) - allowed_domains
        if missing_domains:
            errors.append(
                f"Source {source.source_id} uses information domains absent "
                f"from the taxonomy: {sorted(item.value for item in missing_domains)}."
            )
        for endpoint in source.endpoints:
            if endpoint.access_method not in allowed_methods:
                errors.append(
                    f"Endpoint {endpoint.endpoint_id} uses an access method "
                    "absent from the taxonomy."
                )


def _validate_verified_source(
    source: OfficialSource,
    errors: list[str],
) -> None:
    if source.verification_status is not VerificationStatus.VERIFIED:
        return
    if not source.display_name:
        errors.append(f"VERIFIED source {source.source_id} needs display_name.")
    if not source.provider_name:
        errors.append(f"VERIFIED source {source.source_id} needs provider_name.")
    if source.source_type is SourceType.UNKNOWN:
        errors.append(
            f"VERIFIED source {source.source_id} cannot use source_type UNKNOWN."
        )
    if source.authority_level.value == "UNASSESSED":
        errors.append(
            f"VERIFIED source {source.source_id} needs an assessed authority level."
        )
    if source.officiality_status.value == "UNKNOWN":
        errors.append(
            f"VERIFIED source {source.source_id} needs an officiality status."
        )
    if not source.endpoints:
        errors.append(f"VERIFIED source {source.source_id} needs an endpoint.")
    if not source.verification_rationale:
        errors.append(
            f"VERIFIED source {source.source_id} needs verification_rationale."
        )
    if not source.verification_refs:
        errors.append(
            f"VERIFIED source {source.source_id} needs verification_refs."
        )
    if source.last_verified_at is None:
        errors.append(
            f"VERIFIED source {source.source_id} needs last_verified_at."
        )


def _validate_ready_source(
    source: OfficialSource,
    errors: list[str],
) -> None:
    if source.collection_readiness is not CollectionReadiness.READY:
        return
    if source.record_status is not RecordStatus.ACTIVE:
        errors.append(
            f"READY source {source.source_id} must have record_status ACTIVE."
        )
    if source.verification_status is not VerificationStatus.VERIFIED:
        errors.append(
            f"READY source {source.source_id} must be VERIFIED."
        )
    if source.access_status is not AccessStatus.ACCESSIBLE:
        errors.append(
            f"READY source {source.source_id} must be ACCESSIBLE."
        )
    active_supported = [
        endpoint
        for endpoint in source.endpoints
        if endpoint.endpoint_status is EndpointStatus.ACTIVE
        and endpoint.access_method in SUPPORTED_READY_METHODS
    ]
    if not active_supported:
        errors.append(
            f"READY source {source.source_id} needs an ACTIVE supported endpoint."
        )
    if any(endpoint.requires_auth for endpoint in source.endpoints):
        errors.append(
            f"READY source {source.source_id} cannot require authentication "
            "before a secure integration exists."
        )


def _validate_endpoints(
    sources: SourceRegistry,
    errors: list[str],
) -> int:
    duplicate_count = 0
    global_identities: dict[str, str] = {}
    for source in sources.sources:
        local_identities: set[str] = set()
        for endpoint in source.endpoints:
            if endpoint.url is not None or endpoint.locator is not None:
                expected_id = generate_endpoint_id(
                    source.source_id,
                    url=endpoint.url,
                    locator=endpoint.locator,
                )
                if endpoint.endpoint_id != expected_id:
                    errors.append(
                        f"Endpoint {endpoint.endpoint_id} does not match its "
                        f"deterministic ID {expected_id} for source "
                        f"{source.source_id}."
                    )
            identity = _endpoint_identity(endpoint)
            if identity is None:
                continue
            if identity in local_identities:
                duplicate_count += 1
                errors.append(
                    f"Source {source.source_id} contains duplicate endpoint "
                    f"{endpoint.endpoint_id}."
                )
            local_identities.add(identity)
            other_source = global_identities.get(identity)
            if other_source is not None and other_source != source.source_id:
                duplicate_count += 1
                errors.append(
                    f"Endpoint {identity!r} conflicts between sources "
                    f"{other_source} and {source.source_id}."
                )
            else:
                global_identities[identity] = source.source_id
    return duplicate_count


def _validate_candidates(
    context: CompleteSourceRegistryContext,
    errors: list[str],
    warnings: list[str],
) -> int:
    duplicate_count = 0
    observed_urls: dict[str, list[str]] = defaultdict(list)
    official_source_ids = {
        source.source_id for source in context.sources.sources
    }
    asset_candidate_ids = {
        candidate.candidate_id
        for candidate in context.asset_candidates.candidates
    }
    source_candidate_ids = {
        candidate.candidate_id for candidate in context.candidates.candidates
    }

    for candidate in context.candidates.candidates:
        if candidate.observed_url:
            observed_urls[normalize_url(candidate.observed_url)].append(
                candidate.candidate_id
            )
        missing_asset_candidates = (
            set(candidate.related_asset_candidate_ids) - asset_candidate_ids
        )
        if missing_asset_candidates:
            errors.append(
                f"Source candidate {candidate.candidate_id} references missing "
                f"asset candidates: {sorted(missing_asset_candidates)}."
            )
        if (
            candidate.promoted_source_id is not None
            and candidate.promoted_source_id not in official_source_ids
        ):
            errors.append(
                f"Promoted source candidate {candidate.candidate_id} points "
                f"to missing source {candidate.promoted_source_id}."
            )
        if (
            candidate.duplicate_of_candidate_id is not None
            and candidate.duplicate_of_candidate_id not in source_candidate_ids
        ):
            errors.append(
                f"Duplicate source candidate {candidate.candidate_id} points "
                "to a missing primary candidate."
            )
        if candidate.duplicate_of_candidate_id == candidate.candidate_id:
            errors.append(
                f"Source candidate {candidate.candidate_id} cannot duplicate itself."
            )

    for normalized_url, candidate_ids in sorted(observed_urls.items()):
        if len(candidate_ids) > 1:
            duplicate_count += 1
            warnings.append(
                f"Observed URL {normalized_url!r} is shared by source candidates "
                f"{', '.join(sorted(candidate_ids))}; this is a possible "
                "duplicate, not proof of equal identity."
            )
    return duplicate_count


def _validate_asset_relations(
    context: CompleteSourceRegistryContext,
    errors: list[str],
) -> None:
    official_asset_ids = {
        asset.asset_id for asset in context.asset_registry.assets
    }
    for source in context.sources.sources:
        missing = set(source.related_asset_ids) - official_asset_ids
        if missing:
            errors.append(
                f"Source {source.source_id} references missing official assets: "
                f"{sorted(missing)}."
            )


def _validate_investigation_relations(
    context: CompleteSourceRegistryContext,
    errors: list[str],
) -> None:
    candidate_ids = {
        candidate.candidate_id for candidate in context.candidates.candidates
    }
    for item in context.investigation.items:
        missing = set(item.related_candidate_ids) - candidate_ids
        if missing:
            errors.append(
                f"Investigation {item.investigation_id} references missing "
                f"source candidates: {sorted(missing)}."
            )


def validate_complete_source_context(
    context: CompleteSourceRegistryContext,
) -> SourceRegistryValidationResult:
    """Validate structure and cross-registry Source Registry rules."""

    errors: list[str] = []
    warnings: list[str] = []
    duplicate_count = 0

    _validate_taxonomy(context, errors)
    for source in context.sources.sources:
        _validate_verified_source(source, errors)
        _validate_ready_source(source, errors)
    duplicate_count += _validate_endpoints(context.sources, errors)
    duplicate_count += _validate_candidates(context, errors, warnings)
    _validate_asset_relations(context, errors)
    _validate_investigation_relations(context, errors)

    if errors:
        status = ValidationStatus.FAILED
    elif warnings:
        status = ValidationStatus.PASSED_WITH_WARNINGS
    else:
        status = ValidationStatus.PASSED

    metrics: dict[str, Any] = {
        "registry_version": context.sources.registry_version,
        "candidate_registry_version": (
            context.candidates.candidate_registry_version
        ),
        "investigation_registry_version": (
            context.investigation.investigation_registry_version
        ),
        "candidate_count": len(context.candidates.candidates),
        "source_count": len(context.sources.sources),
        "verified_sources": sum(
            source.verification_status is VerificationStatus.VERIFIED
            for source in context.sources.sources
        ),
        "ready_sources": sum(
            source.collection_readiness is CollectionReadiness.READY
            for source in context.sources.sources
        ),
        "blocked_sources": sum(
            source.collection_readiness is CollectionReadiness.BLOCKED
            for source in context.sources.sources
        ),
        "endpoint_count": sum(
            len(source.endpoints) for source in context.sources.sources
        ),
        "investigation_count": len(context.investigation.items),
        "source_types_used": sorted(
            {source.source_type.value for source in context.sources.sources}
        ),
        "authority_levels_used": sorted(
            {
                source.authority_level.value
                for source in context.sources.sources
            }
        ),
        "duplicate_count": duplicate_count,
        "error_count": len(errors),
        "warning_count": len(warnings),
    }
    return SourceRegistryValidationResult(
        status=status,
        errors=errors,
        warnings=warnings,
        metrics=metrics,
        registry_fingerprint=calculate_context_fingerprint(context),
    )


def write_source_registry_schema(path: str | Path) -> Path:
    """Generate JSON Schema from the Pydantic SourceRegistry model."""

    schema_path = Path(path)
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    schema = SourceRegistry.model_json_schema()
    with schema_path.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(schema, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return schema_path
