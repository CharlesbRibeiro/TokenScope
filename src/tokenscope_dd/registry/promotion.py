"""Atomic in-memory promotion from candidate to official asset."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import ValidationError

from tokenscope_dd.registry.models import (
    AssetCandidate,
    AssetRegistry,
    AssetTaxonomy,
    CandidateRegistry,
    CandidateStatus,
    CompleteRegistryContext,
    EntityInvestigationRegistry,
    OfficialAsset,
    PossibleEntityType,
)
from tokenscope_dd.registry.validation import (
    ValidationStatus,
    validate_complete_registry,
)


class RegistryPromotionError(ValueError):
    """Raised when a candidate cannot be promoted safely."""


@dataclass(frozen=True)
class PromotionResult:
    """New registry values produced by a successful atomic promotion."""

    candidates: CandidateRegistry
    assets: AssetRegistry


def _find_candidate(
    registry: CandidateRegistry,
    candidate_id: str,
) -> tuple[int, AssetCandidate]:
    for index, candidate in enumerate(registry.candidates):
        if candidate.candidate_id == candidate_id:
            return index, candidate
    raise RegistryPromotionError(f"Candidate not found: {candidate_id}")


def promote_candidate(
    *,
    candidate_id: str,
    asset: OfficialAsset,
    taxonomy: AssetTaxonomy,
    candidates: CandidateRegistry,
    assets: AssetRegistry,
    investigation: EntityInvestigationRegistry,
) -> PromotionResult:
    """Promote explicitly supplied identity data without mutating inputs."""

    index, candidate = _find_candidate(candidates, candidate_id)
    if candidate.candidate_status not in {
        CandidateStatus.DISCOVERED,
        CandidateStatus.UNDER_REVIEW,
    }:
        raise RegistryPromotionError(
            f"Candidate {candidate_id} cannot be promoted from "
            f"{candidate.candidate_status.value}."
        )
    if candidate.possible_entity_type is not PossibleEntityType.ASSET:
        raise RegistryPromotionError(
            f"Candidate {candidate_id} is not classified as a possible ASSET."
        )

    promoted_candidate = candidate.model_copy(
        update={
            "candidate_status": CandidateStatus.PROMOTED,
            "promoted_asset_id": asset.asset_id,
        },
        deep=True,
    )
    new_candidate_items = [
        item.model_copy(deep=True) for item in candidates.candidates
    ]
    new_candidate_items[index] = promoted_candidate

    try:
        new_candidates = CandidateRegistry(
            schema_version=candidates.schema_version,
            candidate_registry_version=candidates.candidate_registry_version,
            candidates=new_candidate_items,
        )
        new_assets = AssetRegistry(
            schema_version=assets.schema_version,
            registry_version=assets.registry_version,
            assets=[
                *(item.model_copy(deep=True) for item in assets.assets),
                asset.model_copy(deep=True),
            ],
        )
    except ValidationError as exc:
        raise RegistryPromotionError(
            f"Promotion would create an invalid registry: {exc}"
        ) from exc

    context = CompleteRegistryContext(
        taxonomy=taxonomy.model_copy(deep=True),
        candidates=new_candidates,
        assets=new_assets,
        investigation=investigation.model_copy(deep=True),
    )
    validation = validate_complete_registry(context)
    if validation.status is ValidationStatus.FAILED:
        raise RegistryPromotionError(
            "Promotion failed validation: " + "; ".join(validation.errors)
        )
    return PromotionResult(candidates=new_candidates, assets=new_assets)
