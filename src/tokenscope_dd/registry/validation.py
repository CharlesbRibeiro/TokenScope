"""Cross-document business validation for the Asset Registry."""

from __future__ import annotations

import json
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from tokenscope_dd.registry.fingerprint import (
    calculate_context_fingerprint,
    normalize_identity_text,
)
from tokenscope_dd.registry.models import (
    AssetRegistry,
    CompleteRegistryContext,
    CoverageStatus,
    IdentityStatus,
    OfficialAsset,
    PossibleEntityType,
    RecordStatus,
)


class ValidationStatus(str, Enum):
    """Final status of complete registry validation."""

    PASSED = "PASSED"
    PASSED_WITH_WARNINGS = "PASSED_WITH_WARNINGS"
    FAILED = "FAILED"


class RegistryValidationResult(BaseModel):
    """Machine-readable validation result for terminal and JSON reports."""

    model_config = ConfigDict(extra="forbid")

    status: ValidationStatus
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    registry_fingerprint: str


def _validate_categories(
    context: CompleteRegistryContext,
    errors: list[str],
) -> None:
    categories = {
        category.category_id: category for category in context.taxonomy.categories
    }
    for asset in context.assets.assets:
        category = categories.get(asset.category_id)
        if category is None:
            errors.append(
                f"Asset {asset.asset_id} uses unknown category_id "
                f"{asset.category_id!r}."
            )
            continue
        if not category.active:
            errors.append(
                f"Asset {asset.asset_id} uses inactive category "
                f"{asset.category_id!r}."
            )
        if (
            asset.category_id == "unclassified"
            and asset.coverage_status is CoverageStatus.ANALYSIS_READY
        ):
            errors.append(
                f"Asset {asset.asset_id} cannot be ANALYSIS_READY while "
                "category_id is unclassified."
            )


def _validate_verified_identity(
    asset: OfficialAsset,
    valid_categories: set[str],
    errors: list[str],
) -> None:
    if asset.identity_status is not IdentityStatus.VERIFIED:
        return
    if not asset.official_name:
        errors.append(f"VERIFIED asset {asset.asset_id} needs official_name.")
    if not (asset.issuer_name or asset.issuer_legal_name):
        errors.append(f"VERIFIED asset {asset.asset_id} needs an identified issuer.")
    if (
        asset.category_id not in valid_categories
        or asset.category_id == "unclassified"
    ):
        errors.append(
            f"VERIFIED asset {asset.asset_id} needs a valid classified category."
        )
    if not asset.source_refs:
        errors.append(f"VERIFIED asset {asset.asset_id} needs source_refs.")
    if not asset.identity_rationale:
        errors.append(
            f"VERIFIED asset {asset.asset_id} needs identity_rationale."
        )
    if asset.last_verified_at is None:
        errors.append(f"VERIFIED asset {asset.asset_id} needs last_verified_at.")


def _validate_analysis_ready(
    asset: OfficialAsset,
    errors: list[str],
) -> None:
    if asset.coverage_status is not CoverageStatus.ANALYSIS_READY:
        return
    if asset.record_status is not RecordStatus.ACTIVE:
        errors.append(
            f"ANALYSIS_READY asset {asset.asset_id} must have record_status ACTIVE."
        )
    if asset.identity_status is not IdentityStatus.VERIFIED:
        errors.append(
            f"ANALYSIS_READY asset {asset.asset_id} must have VERIFIED identity."
        )
    if asset.category_id == "unclassified":
        errors.append(
            f"ANALYSIS_READY asset {asset.asset_id} cannot be unclassified."
        )
    if not asset.source_refs:
        errors.append(
            f"ANALYSIS_READY asset {asset.asset_id} must define source_refs."
        )


def _validate_aliases(
    assets: AssetRegistry,
    errors: list[str],
) -> int:
    duplicate_count = 0
    identity_owners: dict[str, str] = {}
    for asset in assets.assets:
        normalized_aliases = [normalize_identity_text(alias) for alias in asset.aliases]
        if len(normalized_aliases) != len(set(normalized_aliases)):
            duplicate_count += 1
            errors.append(f"Asset {asset.asset_id} contains duplicate aliases.")

        identity_values = [asset.official_name, *asset.aliases]
        if asset.short_name:
            identity_values.append(asset.short_name)
        for value in identity_values:
            normalized = normalize_identity_text(value)
            owner = identity_owners.get(normalized)
            if owner is not None and owner != asset.asset_id:
                duplicate_count += 1
                errors.append(
                    f"Identity name or alias {value!r} conflicts between "
                    f"{owner} and {asset.asset_id}."
                )
            else:
                identity_owners[normalized] = asset.asset_id
    return duplicate_count


def _validate_symbols(
    assets: AssetRegistry,
    warnings: list[str],
) -> None:
    owners: dict[str, list[str]] = defaultdict(list)
    for asset in assets.assets:
        if asset.symbol:
            owners[normalize_identity_text(asset.symbol)].append(asset.asset_id)
    for normalized_symbol, asset_ids in sorted(owners.items()):
        if len(asset_ids) > 1:
            warnings.append(
                f"Symbol {normalized_symbol!r} is shared by distinct assets "
                f"{', '.join(sorted(asset_ids))}; symbols are not identity keys."
            )


def _validate_network_contracts(
    assets: AssetRegistry,
    errors: list[str],
) -> int:
    duplicate_count = 0
    global_contracts: dict[tuple[str, str], str] = {}
    for asset in assets.assets:
        local_contracts: set[tuple[str, str]] = set()
        for deployment in asset.network_deployments:
            if deployment.contract_address is None:
                continue
            network = normalize_identity_text(deployment.network_name)
            contract = deployment.contract_address.casefold()
            key = (network, contract)
            if key in local_contracts:
                duplicate_count += 1
                errors.append(
                    f"Asset {asset.asset_id} duplicates contract "
                    f"{deployment.contract_address!r} on "
                    f"{deployment.network_name!r}."
                )
            local_contracts.add(key)
            other_asset = global_contracts.get(key)
            if other_asset is not None and other_asset != asset.asset_id:
                duplicate_count += 1
                errors.append(
                    f"Contract {deployment.contract_address!r} on "
                    f"{deployment.network_name!r} conflicts between "
                    f"{other_asset} and {asset.asset_id}."
                )
            else:
                global_contracts[key] = asset.asset_id
    return duplicate_count


def _validate_candidates(
    context: CompleteRegistryContext,
    errors: list[str],
) -> int:
    duplicate_count = 0
    observations: dict[tuple[str, str], str] = {}
    official_ids = {asset.asset_id for asset in context.assets.assets}
    for candidate in context.candidates.candidates:
        observation = (
            normalize_identity_text(candidate.observed_name),
            normalize_identity_text(candidate.observed_symbol or ""),
        )
        existing = observations.get(observation)
        if existing is not None and existing != candidate.candidate_id:
            duplicate_count += 1
            errors.append(
                f"Candidates {existing} and {candidate.candidate_id} duplicate "
                "the same normalized observation."
            )
        else:
            observations[observation] = candidate.candidate_id

        if candidate.promoted_asset_id is not None:
            if candidate.possible_entity_type is not PossibleEntityType.ASSET:
                errors.append(
                    f"Promoted candidate {candidate.candidate_id} is not typed ASSET."
                )
            if candidate.promoted_asset_id not in official_ids:
                errors.append(
                    f"Promoted candidate {candidate.candidate_id} points to missing "
                    f"asset {candidate.promoted_asset_id}."
                )
    return duplicate_count


def _validate_investigation_separation(
    context: CompleteRegistryContext,
    errors: list[str],
) -> None:
    official_names: dict[str, str] = {}
    for asset in context.assets.assets:
        for value in (asset.official_name, asset.short_name, *asset.aliases):
            if value:
                official_names[normalize_identity_text(value)] = asset.asset_id

    for entity in context.investigation.entities:
        normalized = normalize_identity_text(entity.observed_name)
        if (
            entity.possible_entity_type is not PossibleEntityType.ASSET
            and normalized in official_names
        ):
            errors.append(
                f"Investigated {entity.possible_entity_type.value} "
                f"{entity.observed_name!r} is also registered as official asset "
                f"{official_names[normalized]}."
            )


def validate_complete_registry(
    context: CompleteRegistryContext,
) -> RegistryValidationResult:
    """Validate structural coherence and conditional Asset Registry rules."""

    errors: list[str] = []
    warnings: list[str] = []
    duplicate_count = 0

    valid_categories = {
        category.category_id
        for category in context.taxonomy.categories
        if category.active
    }
    _validate_categories(context, errors)
    for asset in context.assets.assets:
        _validate_verified_identity(asset, valid_categories, errors)
        _validate_analysis_ready(asset, errors)

    duplicate_count += _validate_aliases(context.assets, errors)
    _validate_symbols(context.assets, warnings)
    duplicate_count += _validate_network_contracts(context.assets, errors)
    duplicate_count += _validate_candidates(context, errors)
    _validate_investigation_separation(context, errors)

    if errors:
        status = ValidationStatus.FAILED
    elif warnings:
        status = ValidationStatus.PASSED_WITH_WARNINGS
    else:
        status = ValidationStatus.PASSED

    categories_used = sorted(
        {asset.category_id for asset in context.assets.assets}
    )
    metrics: dict[str, Any] = {
        "registry_version": context.assets.registry_version,
        "candidate_registry_version": (
            context.candidates.candidate_registry_version
        ),
        "investigation_registry_version": (
            context.investigation.investigation_registry_version
        ),
        "candidate_count": len(context.candidates.candidates),
        "asset_count": len(context.assets.assets),
        "verified_assets": sum(
            asset.identity_status is IdentityStatus.VERIFIED
            for asset in context.assets.assets
        ),
        "unverified_assets": sum(
            asset.identity_status is not IdentityStatus.VERIFIED
            for asset in context.assets.assets
        ),
        "analysis_ready_assets": sum(
            asset.coverage_status is CoverageStatus.ANALYSIS_READY
            for asset in context.assets.assets
        ),
        "pending_investigations": sum(
            entity.investigation_status.value in {"PENDING", "UNDER_REVIEW"}
            for entity in context.investigation.entities
        ),
        "categories_used": categories_used,
        "duplicate_count": duplicate_count,
        "error_count": len(errors),
        "warning_count": len(warnings),
    }
    return RegistryValidationResult(
        status=status,
        errors=errors,
        warnings=warnings,
        metrics=metrics,
        registry_fingerprint=calculate_context_fingerprint(context),
    )


def write_asset_registry_schema(path: str | Path) -> Path:
    """Generate the versioned JSON Schema from the Pydantic AssetRegistry model."""

    schema_path = Path(path)
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    schema = AssetRegistry.model_json_schema()
    with schema_path.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(schema, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return schema_path
