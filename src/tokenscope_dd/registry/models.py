"""Pydantic contracts for the TokenScope DD Asset Registry."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)


NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
AssetId = Annotated[
    str,
    StringConstraints(pattern=r"^ts_asset_[0-9a-f]{12}$"),
]
AssetKey = Annotated[
    str,
    StringConstraints(pattern=r"^[a-z0-9]+(?:_[a-z0-9]+)*$"),
]
CandidateId = Annotated[
    str,
    StringConstraints(pattern=r"^ts_candidate_[0-9a-f]{12}$"),
]


class CandidateStatus(str, Enum):
    """Lifecycle states for observations not yet promoted to official assets."""

    DISCOVERED = "DISCOVERED"
    UNDER_REVIEW = "UNDER_REVIEW"
    PROMOTED = "PROMOTED"
    REJECTED = "REJECTED"
    DUPLICATE = "DUPLICATE"


class PossibleEntityType(str, Enum):
    """Possible nature of an observed name before its identity is confirmed."""

    ASSET = "ASSET"
    PLATFORM = "PLATFORM"
    PROTOCOL = "PROTOCOL"
    ISSUER = "ISSUER"
    PLATFORM_OR_PROTOCOL = "PLATFORM_OR_PROTOCOL"
    UNKNOWN = "UNKNOWN"


class RecordStatus(str, Enum):
    """Lifecycle state of an official registry record."""

    CANDIDATE = "CANDIDATE"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"
    REJECTED = "REJECTED"


class IdentityStatus(str, Enum):
    """Confidence state for the identity of an official asset."""

    UNVERIFIED = "UNVERIFIED"
    PROVISIONAL = "PROVISIONAL"
    VERIFIED = "VERIFIED"


class CoverageStatus(str, Enum):
    """Progress of an asset through the future data preparation flow."""

    NOT_STARTED = "NOT_STARTED"
    SOURCES_PENDING = "SOURCES_PENDING"
    SOURCED = "SOURCED"
    CURATED = "CURATED"
    EVIDENCED = "EVIDENCED"
    ANALYSIS_READY = "ANALYSIS_READY"


class DeploymentStatus(str, Enum):
    """Operational state of a network deployment."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DEPRECATED = "DEPRECATED"
    UNKNOWN = "UNKNOWN"


class InvestigationStatus(str, Enum):
    """Lifecycle state of an entity that needs identity investigation."""

    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"


class RegistryModel(BaseModel):
    """Strict base model shared by registry contracts."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class AssetCategory(RegistryModel):
    """A category allowed by the Asset Registry taxonomy."""

    category_id: AssetKey
    display_name: NonEmptyStr
    description: NonEmptyStr
    active: bool


class AssetTaxonomy(RegistryModel):
    """Versioned collection of categories accepted by official assets."""

    schema_version: NonEmptyStr
    categories: list[AssetCategory]

    @model_validator(mode="after")
    def category_ids_must_be_unique(self) -> "AssetTaxonomy":
        ids = [category.category_id for category in self.categories]
        if len(ids) != len(set(ids)):
            raise ValueError("Taxonomy category_id values must be unique.")
        return self


class AssetCandidate(RegistryModel):
    """An observation that has not yet become an official asset."""

    candidate_id: CandidateId
    observed_name: NonEmptyStr
    observed_symbol: NonEmptyStr | None = None
    discovered_in: NonEmptyStr
    discovered_at: date
    possible_entity_type: PossibleEntityType
    candidate_status: CandidateStatus
    notes: NonEmptyStr | None = None
    promoted_asset_id: AssetId | None = None

    @model_validator(mode="after")
    def promoted_reference_must_match_status(self) -> "AssetCandidate":
        if self.candidate_status is CandidateStatus.PROMOTED:
            if self.promoted_asset_id is None:
                raise ValueError(
                    "A PROMOTED candidate must define promoted_asset_id."
                )
        elif self.promoted_asset_id is not None:
            raise ValueError(
                "promoted_asset_id is allowed only when candidate_status is PROMOTED."
            )
        return self


class CandidateRegistry(RegistryModel):
    """Versioned candidate observations preserved before confirmation."""

    schema_version: NonEmptyStr
    candidate_registry_version: NonEmptyStr
    candidates: list[AssetCandidate]

    @model_validator(mode="after")
    def candidate_ids_must_be_unique(self) -> "CandidateRegistry":
        ids = [candidate.candidate_id for candidate in self.candidates]
        if len(ids) != len(set(ids)):
            raise ValueError("candidate_id values must be unique.")
        return self


class NetworkDeployment(RegistryModel):
    """A basic, unverified deployment identity on a named network."""

    network_name: NonEmptyStr
    chain_id: str | None = None
    contract_address: str | None = None
    token_standard: NonEmptyStr | None = None
    deployment_status: DeploymentStatus

    @field_validator("chain_id", mode="before")
    @classmethod
    def normalize_chain_id(cls, value: object) -> str | None:
        if value is None:
            return None
        if isinstance(value, bool):
            raise ValueError("chain_id cannot be a boolean.")
        normalized = str(value).strip()
        return normalized or None

    @field_validator("contract_address", mode="before")
    @classmethod
    def normalize_contract_address(cls, value: object) -> str | None:
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None


class OfficialAsset(RegistryModel):
    """Canonical identity and lifecycle state of an official asset record."""

    asset_id: AssetId = Field(frozen=True)
    asset_key: AssetKey
    official_name: NonEmptyStr
    short_name: NonEmptyStr | None = None
    symbol: NonEmptyStr | None = None
    aliases: list[NonEmptyStr] = Field(default_factory=list)

    category_id: AssetKey
    subcategory_id: AssetKey | None = None
    product_type: NonEmptyStr | None = None
    underlying_asset_type: NonEmptyStr | None = None

    issuer_name: NonEmptyStr | None = None
    issuer_legal_name: NonEmptyStr | None = None
    issuer_reference: NonEmptyStr | None = None

    jurisdictions: list[NonEmptyStr] = Field(default_factory=list)
    official_website: NonEmptyStr | None = None
    launch_date: date | None = None
    currency: NonEmptyStr | None = None

    network_deployments: list[NetworkDeployment] = Field(default_factory=list)

    record_status: RecordStatus
    identity_status: IdentityStatus
    coverage_status: CoverageStatus

    source_refs: list[NonEmptyStr] = Field(default_factory=list)
    identity_rationale: NonEmptyStr | None = None

    schema_version: NonEmptyStr
    created_at: datetime
    updated_at: datetime
    last_verified_at: datetime | None = None
    registry_notes: NonEmptyStr | None = None

    @model_validator(mode="after")
    def updated_at_cannot_precede_created_at(self) -> "OfficialAsset":
        if self.updated_at < self.created_at:
            raise ValueError("updated_at cannot be earlier than created_at.")
        return self


class AssetRegistry(RegistryModel):
    """Versioned official Asset Registry."""

    schema_version: NonEmptyStr
    registry_version: NonEmptyStr
    assets: list[OfficialAsset]

    @model_validator(mode="after")
    def technical_ids_and_keys_must_be_unique(self) -> "AssetRegistry":
        ids = [asset.asset_id for asset in self.assets]
        keys = [asset.asset_key for asset in self.assets]
        if len(ids) != len(set(ids)):
            raise ValueError("asset_id values must be unique.")
        if len(keys) != len(set(keys)):
            raise ValueError("asset_key values must be unique.")
        return self


class InvestigationEntity(RegistryModel):
    """An observed entity kept outside the official asset registry."""

    observed_name: NonEmptyStr
    possible_entity_type: PossibleEntityType
    investigation_status: InvestigationStatus
    reason: NonEmptyStr


class EntityInvestigationRegistry(RegistryModel):
    """Versioned list of names that require entity-type investigation."""

    schema_version: NonEmptyStr
    investigation_registry_version: NonEmptyStr
    entities: list[InvestigationEntity]


class CompleteRegistryContext(RegistryModel):
    """All registry documents required for cross-file validation."""

    taxonomy: AssetTaxonomy
    candidates: CandidateRegistry
    assets: AssetRegistry
    investigation: EntityInvestigationRegistry
