"""Atomic in-memory promotion from source candidate to official source."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import ValidationError

from tokenscope_dd.registry.models import AssetRegistry, CandidateRegistry
from tokenscope_dd.source_registry.models import (
    CandidateStatus,
    CompleteSourceRegistryContext,
    OfficialSource,
    SourceCandidateRegistry,
    SourceInvestigationRegistry,
    SourceRegistry,
    SourceTaxonomy,
)
from tokenscope_dd.source_registry.validation import (
    ValidationStatus,
    validate_complete_source_context,
)


class SourcePromotionError(ValueError):
    """Raised when a source candidate cannot be promoted safely."""


@dataclass(frozen=True)
class SourcePromotionResult:
    candidates: SourceCandidateRegistry
    sources: SourceRegistry


def promote_source_candidate(
    *,
    candidate_id: str,
    source: OfficialSource,
    taxonomy: SourceTaxonomy,
    candidates: SourceCandidateRegistry,
    sources: SourceRegistry,
    investigation: SourceInvestigationRegistry,
    asset_registry: AssetRegistry,
    asset_candidates: CandidateRegistry,
) -> SourcePromotionResult:
    """Promote explicitly supplied source data without mutating inputs."""

    candidate_index = next(
        (
            index
            for index, candidate in enumerate(candidates.candidates)
            if candidate.candidate_id == candidate_id
        ),
        None,
    )
    if candidate_index is None:
        raise SourcePromotionError(f"Source candidate not found: {candidate_id}")
    candidate = candidates.candidates[candidate_index]
    if candidate.candidate_status not in {
        CandidateStatus.DISCOVERED,
        CandidateStatus.UNDER_REVIEW,
    }:
        raise SourcePromotionError(
            f"Source candidate {candidate_id} cannot be promoted from "
            f"{candidate.candidate_status.value}."
        )

    promoted_candidate = candidate.model_copy(
        update={
            "candidate_status": CandidateStatus.PROMOTED,
            "promoted_source_id": source.source_id,
        },
        deep=True,
    )
    candidate_items = [
        item.model_copy(deep=True) for item in candidates.candidates
    ]
    candidate_items[candidate_index] = promoted_candidate

    try:
        new_candidates = SourceCandidateRegistry(
            schema_version=candidates.schema_version,
            candidate_registry_version=candidates.candidate_registry_version,
            candidates=candidate_items,
        )
        new_sources = SourceRegistry(
            schema_version=sources.schema_version,
            registry_version=sources.registry_version,
            sources=[
                *(item.model_copy(deep=True) for item in sources.sources),
                source.model_copy(deep=True),
            ],
        )
    except ValidationError as exc:
        raise SourcePromotionError(
            f"Source promotion would create an invalid registry: {exc}"
        ) from exc

    context = CompleteSourceRegistryContext(
        taxonomy=taxonomy.model_copy(deep=True),
        candidates=new_candidates,
        sources=new_sources,
        investigation=investigation.model_copy(deep=True),
        asset_registry=asset_registry.model_copy(deep=True),
        asset_candidates=asset_candidates.model_copy(deep=True),
    )
    validation = validate_complete_source_context(context)
    if validation.status is ValidationStatus.FAILED:
        raise SourcePromotionError(
            "Source promotion failed validation: "
            + "; ".join(validation.errors)
        )
    return SourcePromotionResult(
        candidates=new_candidates,
        sources=new_sources,
    )
