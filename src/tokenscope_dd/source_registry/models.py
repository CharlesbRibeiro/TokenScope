"""Pydantic contracts for the TokenScope DD Source Registry."""

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

from tokenscope_dd.registry.models import AssetRegistry, CandidateRegistry
from tokenscope_dd.source_registry.normalization import (
    SourceNormalizationError,
    normalize_locator,
    normalize_url,
)


NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
SourceId = Annotated[
    str,
    StringConstraints(pattern=r"^ts_source_[0-9a-f]{12}$"),
]
SourceKey = Annotated[
    str,
    StringConstraints(pattern=r"^[a-z0-9]+(?:_[a-z0-9]+)*$"),
]
SourceCandidateId = Annotated[
    str,
    StringConstraints(pattern=r"^ts_source_candidate_[0-9a-f]{12}$"),
]
EndpointId = Annotated[
    str,
    StringConstraints(pattern=r"^ts_endpoint_[0-9a-f]{12}$"),
]
InvestigationId = Annotated[
    str,
    StringConstraints(pattern=r"^ts_source_investigation_[0-9a-f]{12}$"),
]


class SourceType(str, Enum):
    OFFICIAL_PRODUCT_PAGE = "OFFICIAL_PRODUCT_PAGE"
    OFFICIAL_DOCUMENT = "OFFICIAL_DOCUMENT"
    REGULATOR = "REGULATOR"
    AUDITOR_OR_ATTESTATION = "AUDITOR_OR_ATTESTATION"
    BLOCKCHAIN_EXPLORER = "BLOCKCHAIN_EXPLORER"
    TECHNICAL_DOCUMENTATION = "TECHNICAL_DOCUMENTATION"
    DATA_PROVIDER = "DATA_PROVIDER"
    RESEARCH_REPORT = "RESEARCH_REPORT"
    NEWS = "NEWS"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class AuthorityLevel(str, Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    TERTIARY = "TERTIARY"
    UNASSESSED = "UNASSESSED"


class OfficialityStatus(str, Enum):
    OFFICIAL = "OFFICIAL"
    INDEPENDENT = "INDEPENDENT"
    AGGREGATOR = "AGGREGATOR"
    COMMUNITY = "COMMUNITY"
    UNKNOWN = "UNKNOWN"


class InformationDomain(str, Enum):
    IDENTITY = "IDENTITY"
    LEGAL = "LEGAL"
    REGULATORY = "REGULATORY"
    STRUCTURE = "STRUCTURE"
    ISSUER = "ISSUER"
    FEES = "FEES"
    LIQUIDITY = "LIQUIDITY"
    HOLDERS = "HOLDERS"
    TRANSACTIONS = "TRANSACTIONS"
    HOLDINGS = "HOLDINGS"
    RESERVES = "RESERVES"
    ATTESTATION = "ATTESTATION"
    PERFORMANCE = "PERFORMANCE"
    OPERATIONS = "OPERATIONS"
    TECHNICAL = "TECHNICAL"
    NETWORK = "NETWORK"
    OTHER = "OTHER"


class AccessMethod(str, Enum):
    HTTP_HTML = "HTTP_HTML"
    HTTP_PDF = "HTTP_PDF"
    HTTP_JSON = "HTTP_JSON"
    API = "API"
    FILE = "FILE"
    MANUAL = "MANUAL"
    BLOCKCHAIN_EXPLORER = "BLOCKCHAIN_EXPLORER"
    OTHER = "OTHER"


class CandidateStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    UNDER_REVIEW = "UNDER_REVIEW"
    PROMOTED = "PROMOTED"
    REJECTED = "REJECTED"
    DUPLICATE = "DUPLICATE"


class EndpointRole(str, Enum):
    LANDING_PAGE = "LANDING_PAGE"
    PRODUCT_PAGE = "PRODUCT_PAGE"
    DOCUMENT = "DOCUMENT"
    DOWNLOAD = "DOWNLOAD"
    API = "API"
    DATA_PAGE = "DATA_PAGE"
    EXPLORER = "EXPLORER"
    OTHER = "OTHER"


class EndpointStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DEPRECATED = "DEPRECATED"
    UNKNOWN = "UNKNOWN"


class ContentType(str, Enum):
    HTML = "HTML"
    PDF = "PDF"
    JSON = "JSON"
    CSV = "CSV"
    XML = "XML"
    TEXT = "TEXT"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class RecordStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"
    REJECTED = "REJECTED"


class VerificationStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    PROVISIONAL = "PROVISIONAL"
    VERIFIED = "VERIFIED"


class AccessStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    ACCESSIBLE = "ACCESSIBLE"
    RESTRICTED = "RESTRICTED"
    UNAVAILABLE = "UNAVAILABLE"
    DEPRECATED = "DEPRECATED"


class CollectionReadiness(str, Enum):
    NOT_READY = "NOT_READY"
    READY = "READY"
    BLOCKED = "BLOCKED"
    RETIRED = "RETIRED"


class InvestigationStatus(str, Enum):
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"


class PossibleSourceEntityType(str, Enum):
    PROVIDER = "PROVIDER"
    DOMAIN = "DOMAIN"
    PLATFORM = "PLATFORM"
    PAGE = "PAGE"
    DOCUMENT = "DOCUMENT"
    API = "API"
    AGGREGATOR = "AGGREGATOR"
    DUPLICATE_SOURCE = "DUPLICATE_SOURCE"
    UNKNOWN = "UNKNOWN"


class SourceRegistryModel(BaseModel):
    """Strict base model shared by source registry contracts."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class SourceTaxonomy(SourceRegistryModel):
    """Versioned values permitted in source classification."""

    schema_version: NonEmptyStr
    source_types: list[SourceType]
    authority_levels: list[AuthorityLevel]
    officiality_statuses: list[OfficialityStatus]
    information_domains: list[InformationDomain]
    access_methods: list[AccessMethod]
    descriptions: dict[str, NonEmptyStr]

    @model_validator(mode="after")
    def taxonomy_values_must_be_unique_and_described(self) -> "SourceTaxonomy":
        collections = (
            self.source_types,
            self.authority_levels,
            self.officiality_statuses,
            self.information_domains,
            self.access_methods,
        )
        if any(len(values) != len(set(values)) for values in collections):
            raise ValueError("Taxonomy values must be unique within each group.")
        required_descriptions = {
            "source_types",
            "authority_levels",
            "officiality_statuses",
            "information_domains",
            "access_methods",
        }
        if set(self.descriptions) != required_descriptions:
            raise ValueError(
                "Taxonomy descriptions must cover exactly the five value groups."
            )
        return self


class SourceCandidate(SourceRegistryModel):
    """A locally observed source that is not yet official."""

    candidate_id: SourceCandidateId
    observed_name: NonEmptyStr
    observed_url: NonEmptyStr | None = None
    observed_provider: NonEmptyStr | None = None
    discovered_in: NonEmptyStr
    discovered_at: date
    possible_source_type: SourceType
    candidate_status: CandidateStatus
    related_asset_candidate_ids: list[NonEmptyStr] = Field(default_factory=list)
    notes: NonEmptyStr | None = None
    promoted_source_id: SourceId | None = None
    duplicate_of_candidate_id: SourceCandidateId | None = None

    @field_validator("observed_url")
    @classmethod
    def observed_url_must_be_safe(cls, value: str | None) -> str | None:
        if value is not None:
            normalize_url(value)
        return value

    @model_validator(mode="after")
    def lifecycle_references_must_match_status(self) -> "SourceCandidate":
        if self.candidate_status is CandidateStatus.PROMOTED:
            if self.promoted_source_id is None:
                raise ValueError(
                    "A PROMOTED candidate must define promoted_source_id."
                )
        elif self.promoted_source_id is not None:
            raise ValueError(
                "promoted_source_id is allowed only for PROMOTED candidates."
            )
        if self.candidate_status is CandidateStatus.DUPLICATE:
            if self.duplicate_of_candidate_id is None:
                raise ValueError(
                    "A DUPLICATE candidate must define duplicate_of_candidate_id."
                )
        elif self.duplicate_of_candidate_id is not None:
            raise ValueError(
                "duplicate_of_candidate_id is allowed only for DUPLICATE candidates."
            )
        return self


class SourceCandidateRegistry(SourceRegistryModel):
    schema_version: NonEmptyStr
    candidate_registry_version: NonEmptyStr
    candidates: list[SourceCandidate]

    @model_validator(mode="after")
    def candidate_ids_must_be_unique(self) -> "SourceCandidateRegistry":
        ids = [candidate.candidate_id for candidate in self.candidates]
        if len(ids) != len(set(ids)):
            raise ValueError("Source candidate_id values must be unique.")
        return self


class SourceEndpoint(SourceRegistryModel):
    """A concrete address used to access information from a source."""

    endpoint_id: EndpointId = Field(frozen=True)
    url: NonEmptyStr | None = None
    locator: NonEmptyStr | None = None
    endpoint_role: EndpointRole
    access_method: AccessMethod
    content_type: ContentType
    endpoint_status: EndpointStatus
    requires_auth: bool
    notes: NonEmptyStr | None = None

    @model_validator(mode="after")
    def access_identity_must_match_method(self) -> "SourceEndpoint":
        url_methods = {
            AccessMethod.HTTP_HTML,
            AccessMethod.HTTP_PDF,
            AccessMethod.HTTP_JSON,
            AccessMethod.API,
            AccessMethod.BLOCKCHAIN_EXPLORER,
        }
        try:
            if self.access_method in url_methods:
                if self.url is None:
                    raise ValueError(
                        f"{self.access_method.value} endpoint requires url."
                    )
                normalize_url(self.url)
            elif self.access_method is AccessMethod.FILE:
                if self.locator is None:
                    raise ValueError("FILE endpoint requires locator.")
                normalize_locator(self.locator)
        except SourceNormalizationError as exc:
            raise ValueError(str(exc)) from exc
        if self.url is not None and self.locator is not None:
            raise ValueError("Endpoint cannot define both url and locator.")
        return self


class OfficialSource(SourceRegistryModel):
    """Canonical identity and governance state of an official source."""

    source_id: SourceId = Field(frozen=True)
    source_key: SourceKey
    display_name: NonEmptyStr
    provider_name: NonEmptyStr | None = None
    provider_domain: NonEmptyStr | None = None

    source_type: SourceType
    authority_level: AuthorityLevel
    officiality_status: OfficialityStatus
    information_domains: list[InformationDomain] = Field(default_factory=list)
    related_asset_ids: list[NonEmptyStr] = Field(default_factory=list)

    endpoints: list[SourceEndpoint] = Field(default_factory=list)
    access_status: AccessStatus
    collection_readiness: CollectionReadiness

    record_status: RecordStatus
    verification_status: VerificationStatus

    verification_rationale: NonEmptyStr | None = None
    verification_refs: list[NonEmptyStr] = Field(default_factory=list)
    usage_restrictions: NonEmptyStr | None = None
    terms_notes: NonEmptyStr | None = None
    expected_update_frequency: NonEmptyStr | None = None
    expected_refresh_days: int | None = Field(default=None, ge=1)

    schema_version: NonEmptyStr
    created_at: datetime
    updated_at: datetime
    last_verified_at: datetime | None = None
    registry_notes: NonEmptyStr | None = None

    @model_validator(mode="after")
    def source_internal_rules(self) -> "OfficialSource":
        if self.updated_at < self.created_at:
            raise ValueError("updated_at cannot be earlier than created_at.")
        endpoint_ids = [endpoint.endpoint_id for endpoint in self.endpoints]
        if len(endpoint_ids) != len(set(endpoint_ids)):
            raise ValueError("endpoint_id values must be unique within a source.")
        return self


class SourceRegistry(SourceRegistryModel):
    schema_version: NonEmptyStr
    registry_version: NonEmptyStr
    sources: list[OfficialSource]

    @model_validator(mode="after")
    def source_ids_and_keys_must_be_unique(self) -> "SourceRegistry":
        ids = [source.source_id for source in self.sources]
        keys = [source.source_key for source in self.sources]
        if len(ids) != len(set(ids)):
            raise ValueError("source_id values must be unique.")
        if len(keys) != len(set(keys)):
            raise ValueError("source_key values must be unique.")
        return self


class SourceInvestigationItem(SourceRegistryModel):
    investigation_id: InvestigationId
    observed_value: NonEmptyStr
    possible_entity_type: PossibleSourceEntityType
    discovered_in: NonEmptyStr
    investigation_status: InvestigationStatus
    reason: NonEmptyStr
    related_candidate_ids: list[SourceCandidateId] = Field(default_factory=list)
    notes: NonEmptyStr | None = None


class SourceInvestigationRegistry(SourceRegistryModel):
    schema_version: NonEmptyStr
    investigation_registry_version: NonEmptyStr
    items: list[SourceInvestigationItem]

    @model_validator(mode="after")
    def investigation_ids_must_be_unique(self) -> "SourceInvestigationRegistry":
        ids = [item.investigation_id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("investigation_id values must be unique.")
        return self


class CompleteSourceRegistryContext(SourceRegistryModel):
    """All source and asset documents needed for cross-validation."""

    taxonomy: SourceTaxonomy
    candidates: SourceCandidateRegistry
    sources: SourceRegistry
    investigation: SourceInvestigationRegistry
    asset_registry: AssetRegistry
    asset_candidates: CandidateRegistry
