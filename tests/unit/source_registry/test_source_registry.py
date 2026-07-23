"""Unit and local integration tests for the Source Registry."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from tokenscope_dd.registry.loader import (
    load_asset_candidates,
    load_asset_registry,
)
from tokenscope_dd.source_registry import (
    AccessMethod,
    AccessStatus,
    AuthorityLevel,
    CandidateStatus,
    CollectionReadiness,
    CompleteSourceRegistryContext,
    ContentType,
    EndpointRole,
    EndpointStatus,
    InformationDomain,
    OfficialityStatus,
    OfficialSource,
    RecordStatus,
    SourceCandidate,
    SourceCandidateRegistry,
    SourceEndpoint,
    SourceInvestigationRegistry,
    SourceNormalizationError,
    SourcePromotionError,
    SourceRegistry,
    SourceRegistryLoadError,
    SourceTaxonomy,
    SourceType,
    ValidationStatus,
    VerificationStatus,
    calculate_registry_fingerprint,
    canonical_registry_json,
    generate_endpoint_id,
    generate_source_candidate_id,
    load_complete_source_context,
    load_source_candidates,
    load_source_investigation,
    load_source_registry,
    load_source_taxonomy,
    normalize_url,
    promote_source_candidate,
    validate_complete_source_context,
    write_source_registry_schema,
)


ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "tests" / "fixtures" / "source_registry"
ASSET_REGISTRY = ROOT / "configs" / "registries" / "assets.yaml"
ASSET_CANDIDATES = ROOT / "configs" / "registries" / "asset_candidates.yaml"
NOW = datetime(2026, 7, 23, 12, 0, tzinfo=timezone.utc)


def make_endpoint(
    index: int = 1,
    *,
    source_id: str = "ts_source_000000000001",
    url: str | None = "https://example.com/data",
    locator: str | None = None,
    access_method: AccessMethod = AccessMethod.HTTP_HTML,
    endpoint_status: EndpointStatus = EndpointStatus.ACTIVE,
    requires_auth: bool = False,
) -> SourceEndpoint:
    endpoint_id = generate_endpoint_id(
        source_id,
        url=url,
        locator=locator,
    )
    return SourceEndpoint(
        endpoint_id=endpoint_id,
        url=url,
        locator=locator,
        endpoint_role=EndpointRole.DATA_PAGE,
        access_method=access_method,
        content_type=ContentType.HTML,
        endpoint_status=endpoint_status,
        requires_auth=requires_auth,
        notes=None,
    )


def source_payload(index: int = 1) -> dict[str, object]:
    source_id = f"ts_source_{index:012x}"
    return {
        "source_id": source_id,
        "source_key": f"source_{index}",
        "display_name": f"Source {index}",
        "provider_name": f"Provider {index}",
        "provider_domain": "example.com",
        "source_type": SourceType.DATA_PROVIDER,
        "authority_level": AuthorityLevel.PRIMARY,
        "officiality_status": OfficialityStatus.INDEPENDENT,
        "information_domains": [InformationDomain.IDENTITY],
        "related_asset_ids": [],
        "endpoints": [make_endpoint(source_id=source_id)],
        "access_status": AccessStatus.UNKNOWN,
        "collection_readiness": CollectionReadiness.NOT_READY,
        "record_status": RecordStatus.ACTIVE,
        "verification_status": VerificationStatus.UNVERIFIED,
        "verification_rationale": None,
        "verification_refs": [],
        "usage_restrictions": None,
        "terms_notes": None,
        "expected_update_frequency": None,
        "expected_refresh_days": None,
        "schema_version": "1.0.0",
        "created_at": NOW,
        "updated_at": NOW,
        "last_verified_at": None,
        "registry_notes": None,
    }


def make_source(index: int = 1, **updates: object) -> OfficialSource:
    payload = source_payload(index)
    payload.update(updates)
    return OfficialSource.model_validate(payload)


def make_candidate(index: int = 1, **updates: object) -> SourceCandidate:
    payload: dict[str, object] = {
        "candidate_id": f"ts_source_candidate_{index:012x}",
        "observed_name": f"Observed Source {index}",
        "observed_url": f"https://example.com/source-{index}",
        "observed_provider": f"Provider {index}",
        "discovered_in": "local_fixture.yaml",
        "discovered_at": "2026-07-21",
        "possible_source_type": SourceType.DATA_PROVIDER,
        "candidate_status": CandidateStatus.DISCOVERED,
        "related_asset_candidate_ids": [],
        "notes": None,
        "promoted_source_id": None,
        "duplicate_of_candidate_id": None,
    }
    payload.update(updates)
    return SourceCandidate.model_validate(payload)


def make_context(
    *,
    sources: list[OfficialSource] | None = None,
    candidates: list[SourceCandidate] | None = None,
    taxonomy: SourceTaxonomy | None = None,
) -> CompleteSourceRegistryContext:
    return CompleteSourceRegistryContext(
        taxonomy=taxonomy or load_source_taxonomy(FIXTURES / "taxonomy_valid.yaml"),
        candidates=SourceCandidateRegistry(
            schema_version="1.0.0",
            candidate_registry_version="0.1.0",
            candidates=candidates or [],
        ),
        sources=SourceRegistry(
            schema_version="1.0.0",
            registry_version="0.1.0",
            sources=sources or [],
        ),
        investigation=SourceInvestigationRegistry(
            schema_version="1.0.0",
            investigation_registry_version="0.1.0",
            items=[],
        ),
        asset_registry=load_asset_registry(ASSET_REGISTRY),
        asset_candidates=load_asset_candidates(ASSET_CANDIDATES),
    )


def verified_updates() -> dict[str, object]:
    return {
        "verification_status": VerificationStatus.VERIFIED,
        "verification_rationale": "Identity confirmed by local approved records.",
        "verification_refs": ["local-approved-reference"],
        "last_verified_at": NOW,
    }


def test_load_source_taxonomy() -> None:
    taxonomy = load_source_taxonomy(FIXTURES / "taxonomy_valid.yaml")
    assert SourceType.DATA_PROVIDER in taxonomy.source_types
    assert AccessMethod.FILE in taxonomy.access_methods


def test_load_empty_source_registry() -> None:
    registry = load_source_registry(FIXTURES / "sources_empty.yaml")
    assert registry.sources == []


def test_load_source_candidates() -> None:
    registry = load_source_candidates(FIXTURES / "candidates_valid.yaml")
    assert len(registry.candidates) == 1
    assert registry.candidates[0].candidate_status is CandidateStatus.DISCOVERED


def test_load_empty_source_investigation() -> None:
    registry = load_source_investigation(
        FIXTURES / "investigation_empty.yaml"
    )
    assert registry.items == []


def test_empty_registry_context_is_valid() -> None:
    result = validate_complete_source_context(make_context())
    assert result.status is ValidationStatus.PASSED
    assert result.errors == []


def test_empty_registry_fingerprint_is_stable() -> None:
    registry = load_source_registry(FIXTURES / "sources_empty.yaml")
    assert calculate_registry_fingerprint(registry) == (
        calculate_registry_fingerprint(registry.model_copy(deep=True))
    )
    assert len(calculate_registry_fingerprint(registry)) == 64


def test_reject_duplicate_source_id() -> None:
    first = make_source(1)
    second = make_source(2).model_copy(update={"source_id": first.source_id})
    with pytest.raises(ValidationError, match="source_id values must be unique"):
        SourceRegistry(
            schema_version="1.0.0",
            registry_version="0.1.0",
            sources=[first, second],
        )


def test_reject_duplicate_source_key() -> None:
    first = make_source(1)
    second = make_source(2).model_copy(update={"source_key": first.source_key})
    with pytest.raises(ValidationError, match="source_key values must be unique"):
        SourceRegistry(
            schema_version="1.0.0",
            registry_version="0.1.0",
            sources=[first, second],
        )


def test_source_id_is_immutable() -> None:
    source = make_source()
    with pytest.raises(ValidationError, match="Field is frozen"):
        source.source_id = "ts_source_000000000002"


def test_reject_duplicate_candidate_id() -> None:
    candidate = make_candidate()
    with pytest.raises(
        ValidationError,
        match="candidate_id values must be unique",
    ):
        SourceCandidateRegistry(
            schema_version="1.0.0",
            candidate_registry_version="0.1.0",
            candidates=[candidate, candidate.model_copy(deep=True)],
        )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (" HTTPS://Example.COM:443 ", "https://example.com/"),
        ("http://EXAMPLE.com:80/path/", "http://example.com/path"),
        ("https://example.com/path#section", "https://example.com/path"),
    ],
)
def test_normalize_url_safely(value: str, expected: str) -> None:
    assert normalize_url(value) == expected


def test_url_original_is_preserved() -> None:
    original = "HTTPS://Example.COM/Path/#fragment"
    endpoint = make_endpoint(url=original)
    assert endpoint.url == original
    assert normalize_url(endpoint.url) == "https://example.com/Path"


def test_query_is_preserved_safely() -> None:
    value = "https://example.com/data?signature=A%2FB&x=1#fragment"
    assert normalize_url(value) == (
        "https://example.com/data?signature=A%2FB&x=1"
    )


@pytest.mark.parametrize("value", ["ftp://example.com", "file:///tmp/a"])
def test_reject_unapproved_url_scheme(value: str) -> None:
    with pytest.raises(SourceNormalizationError, match="not allowed"):
        normalize_url(value)


def test_reject_credentials_embedded_in_url() -> None:
    with pytest.raises(SourceNormalizationError, match="Credentials"):
        normalize_url("https://user:password@example.com/data")


def test_reject_http_endpoint_without_url() -> None:
    with pytest.raises(ValidationError, match="requires url"):
        SourceEndpoint(
            endpoint_id="ts_endpoint_000000000001",
            url=None,
            locator=None,
            endpoint_role=EndpointRole.DATA_PAGE,
            access_method=AccessMethod.HTTP_HTML,
            content_type=ContentType.HTML,
            endpoint_status=EndpointStatus.ACTIVE,
            requires_auth=False,
            notes=None,
        )


def test_reject_file_endpoint_without_locator() -> None:
    with pytest.raises(ValidationError, match="requires locator"):
        SourceEndpoint(
            endpoint_id="ts_endpoint_000000000001",
            url=None,
            locator=None,
            endpoint_role=EndpointRole.DOCUMENT,
            access_method=AccessMethod.FILE,
            content_type=ContentType.PDF,
            endpoint_status=EndpointStatus.ACTIVE,
            requires_auth=False,
            notes=None,
        )


def test_reject_duplicate_endpoint_within_source() -> None:
    endpoint = make_endpoint()
    source = make_source(
        endpoints=[
            endpoint,
            endpoint.model_copy(
                update={"endpoint_id": "ts_endpoint_000000000002"}
            ),
        ]
    )
    result = validate_complete_source_context(make_context(sources=[source]))
    assert result.status is ValidationStatus.FAILED
    assert any("duplicate endpoint" in error for error in result.errors)


def test_reject_endpoint_conflict_between_sources() -> None:
    first = make_source(1)
    second = make_source(
        2,
        endpoints=[
            make_endpoint(
                2,
                source_id="ts_source_000000000002",
                url="HTTPS://EXAMPLE.COM/data#other",
            )
        ],
    )
    result = validate_complete_source_context(
        make_context(sources=[first, second])
    )
    assert result.status is ValidationStatus.FAILED
    assert any("conflicts between sources" in error for error in result.errors)


def test_reject_endpoint_id_not_derived_from_source_and_url() -> None:
    endpoint = make_endpoint().model_copy(
        update={"endpoint_id": "ts_endpoint_000000000002"}
    )
    source = make_source(endpoints=[endpoint])
    result = validate_complete_source_context(make_context(sources=[source]))
    assert result.status is ValidationStatus.FAILED
    assert any("does not match its deterministic ID" in error for error in result.errors)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source_type", "INVALID"),
        ("authority_level", "INVALID"),
        ("officiality_status", "INVALID"),
        ("information_domains", ["INVALID"]),
    ],
)
def test_reject_invalid_classification_values(
    field: str,
    value: object,
) -> None:
    payload = source_payload()
    payload[field] = value
    with pytest.raises(ValidationError):
        OfficialSource.model_validate(payload)


def test_reject_verified_without_endpoint() -> None:
    source = make_source(endpoints=[], **verified_updates())
    result = validate_complete_source_context(make_context(sources=[source]))
    assert any("needs an endpoint" in error for error in result.errors)


def test_reject_verified_without_provider() -> None:
    source = make_source(provider_name=None, **verified_updates())
    result = validate_complete_source_context(make_context(sources=[source]))
    assert any("needs provider_name" in error for error in result.errors)


def test_reject_verified_without_rationale() -> None:
    updates = verified_updates()
    updates["verification_rationale"] = None
    source = make_source(**updates)
    result = validate_complete_source_context(make_context(sources=[source]))
    assert any("verification_rationale" in error for error in result.errors)


def test_reject_verified_without_references() -> None:
    updates = verified_updates()
    updates["verification_refs"] = []
    source = make_source(**updates)
    result = validate_complete_source_context(make_context(sources=[source]))
    assert any("verification_refs" in error for error in result.errors)


def test_reject_verified_without_last_verified_at() -> None:
    updates = verified_updates()
    updates["last_verified_at"] = None
    source = make_source(**updates)
    result = validate_complete_source_context(make_context(sources=[source]))
    assert any("last_verified_at" in error for error in result.errors)


def test_reject_ready_without_verified() -> None:
    source = make_source(
        collection_readiness=CollectionReadiness.READY,
        access_status=AccessStatus.ACCESSIBLE,
    )
    result = validate_complete_source_context(make_context(sources=[source]))
    assert any("must be VERIFIED" in error for error in result.errors)


def test_reject_ready_without_access() -> None:
    source = make_source(
        collection_readiness=CollectionReadiness.READY,
        access_status=AccessStatus.UNKNOWN,
        **verified_updates(),
    )
    result = validate_complete_source_context(make_context(sources=[source]))
    assert any("must be ACCESSIBLE" in error for error in result.errors)


def test_reject_ready_without_active_endpoint() -> None:
    source = make_source(
        endpoints=[
            make_endpoint(endpoint_status=EndpointStatus.DEPRECATED)
        ],
        collection_readiness=CollectionReadiness.READY,
        access_status=AccessStatus.ACCESSIBLE,
        **verified_updates(),
    )
    result = validate_complete_source_context(make_context(sources=[source]))
    assert any("ACTIVE supported endpoint" in error for error in result.errors)


def test_authenticated_source_cannot_be_ready() -> None:
    source = make_source(
        endpoints=[make_endpoint(requires_auth=True)],
        collection_readiness=CollectionReadiness.READY,
        access_status=AccessStatus.ACCESSIBLE,
        **verified_updates(),
    )
    result = validate_complete_source_context(make_context(sources=[source]))
    assert any("require authentication" in error for error in result.errors)


def test_valid_ready_source_is_accepted() -> None:
    source = make_source(
        collection_readiness=CollectionReadiness.READY,
        access_status=AccessStatus.ACCESSIBLE,
        **verified_updates(),
    )
    result = validate_complete_source_context(make_context(sources=[source]))
    assert result.status is ValidationStatus.PASSED


def test_valid_relation_to_asset_candidate() -> None:
    asset_candidate_id = load_asset_candidates(
        ASSET_CANDIDATES
    ).candidates[0].candidate_id
    candidate = make_candidate(
        related_asset_candidate_ids=[asset_candidate_id]
    )
    result = validate_complete_source_context(
        make_context(candidates=[candidate])
    )
    assert result.status is ValidationStatus.PASSED


def test_reject_missing_asset_candidate_relation() -> None:
    candidate = make_candidate(
        related_asset_candidate_ids=["ts_candidate_000000000000"]
    )
    result = validate_complete_source_context(
        make_context(candidates=[candidate])
    )
    assert any("missing asset candidates" in error for error in result.errors)


def test_reject_missing_official_asset_relation() -> None:
    source = make_source(related_asset_ids=["ts_asset_000000000001"])
    result = validate_complete_source_context(make_context(sources=[source]))
    assert any("missing official assets" in error for error in result.errors)


def test_reject_promoted_candidate_pointing_to_missing_source() -> None:
    candidate = make_candidate(
        candidate_status=CandidateStatus.PROMOTED,
        promoted_source_id="ts_source_000000000001",
    )
    result = validate_complete_source_context(
        make_context(candidates=[candidate])
    )
    assert any("points to missing source" in error for error in result.errors)


def test_promote_source_candidate_safely_without_mutation() -> None:
    candidate = make_candidate()
    candidates = SourceCandidateRegistry(
        schema_version="1.0.0",
        candidate_registry_version="0.1.0",
        candidates=[candidate],
    )
    source = make_source()
    context = make_context()
    result = promote_source_candidate(
        candidate_id=candidate.candidate_id,
        source=source,
        taxonomy=context.taxonomy,
        candidates=candidates,
        sources=context.sources,
        investigation=context.investigation,
        asset_registry=context.asset_registry,
        asset_candidates=context.asset_candidates,
    )
    assert candidate.candidate_status is CandidateStatus.DISCOVERED
    assert context.sources.sources == []
    assert result.candidates.candidates[0].candidate_status is CandidateStatus.PROMOTED
    assert result.sources.sources[0].source_id == source.source_id


def test_failed_promotion_has_no_partial_change() -> None:
    candidate = make_candidate()
    candidates = SourceCandidateRegistry(
        schema_version="1.0.0",
        candidate_registry_version="0.1.0",
        candidates=[candidate],
    )
    invalid_source = make_source(
        related_asset_ids=["ts_asset_000000000001"]
    )
    context = make_context()
    with pytest.raises(SourcePromotionError, match="failed validation"):
        promote_source_candidate(
            candidate_id=candidate.candidate_id,
            source=invalid_source,
            taxonomy=context.taxonomy,
            candidates=candidates,
            sources=context.sources,
            investigation=context.investigation,
            asset_registry=context.asset_registry,
            asset_candidates=context.asset_candidates,
        )
    assert candidates.candidates[0].candidate_status is CandidateStatus.DISCOVERED
    assert context.sources.sources == []


def test_rejected_candidate_is_preserved() -> None:
    candidate = make_candidate(candidate_status=CandidateStatus.REJECTED)
    registry = SourceCandidateRegistry(
        schema_version="1.0.0",
        candidate_registry_version="0.1.0",
        candidates=[candidate],
    )
    assert registry.candidates[0].candidate_status is CandidateStatus.REJECTED


def test_archived_source_is_preserved() -> None:
    source = make_source(record_status=RecordStatus.ARCHIVED)
    result = validate_complete_source_context(make_context(sources=[source]))
    assert result.status is ValidationStatus.PASSED


def test_deprecated_endpoint_is_preserved() -> None:
    endpoint = make_endpoint(endpoint_status=EndpointStatus.DEPRECATED)
    source = make_source(endpoints=[endpoint])
    assert source.endpoints[0].endpoint_status is EndpointStatus.DEPRECATED


def test_candidate_id_is_deterministic() -> None:
    expected = generate_source_candidate_id(
        "RWA.xyz",
        "https://app.rwa.xyz",
        "RWA.xyz",
        "configs/sources.example.yaml",
    )
    repeated = generate_source_candidate_id(
        " rwa.XYZ ",
        "HTTPS://APP.RWA.XYZ/",
        "rwa.xyz",
        "configs/sources.example.yaml",
    )
    assert expected == repeated == "ts_source_candidate_096f8d408ac9"


def test_endpoint_id_is_deterministic() -> None:
    first = generate_endpoint_id(
        "ts_source_000000000001",
        url="https://example.com/data#first",
    )
    second = generate_endpoint_id(
        "ts_source_000000000001",
        url="HTTPS://EXAMPLE.COM:443/data/",
    )
    assert first == second


def test_asset_name_is_not_source_identity() -> None:
    first = make_source(
        1,
        display_name="BUIDL",
        endpoints=[make_endpoint(1, url="https://example.com/first")],
    )
    second = make_source(
        2,
        display_name="BUIDL",
        endpoints=[
            make_endpoint(
                2,
                source_id="ts_source_000000000002",
                url="https://example.com/second",
            )
        ],
    )
    result = validate_complete_source_context(
        make_context(sources=[first, second])
    )
    assert result.status is ValidationStatus.PASSED


def test_canonical_serialization_is_deterministic() -> None:
    first = make_source(
        1,
        information_domains=[
            InformationDomain.PERFORMANCE,
            InformationDomain.IDENTITY,
        ],
        endpoints=[
            make_endpoint(2, url="https://example.com/second"),
            make_endpoint(1, url="https://example.com/first"),
        ],
    )
    second = make_source(2)
    registry_a = SourceRegistry(
        schema_version="1.0.0",
        registry_version="0.1.0",
        sources=[second, first],
    )
    registry_b = SourceRegistry(
        schema_version="1.0.0",
        registry_version="0.1.0",
        sources=[first, second],
    )
    assert canonical_registry_json(registry_a) == canonical_registry_json(
        registry_b
    )


def test_fingerprint_equal_for_equivalent_yaml_formatting() -> None:
    compact = """
schema_version: 1.0.0
registry_version: 0.1.0
sources: []
"""
    inline = "{sources: [], registry_version: 0.1.0, schema_version: 1.0.0}"
    first = SourceRegistry.model_validate(yaml.safe_load(compact))
    second = SourceRegistry.model_validate(yaml.safe_load(inline))
    assert calculate_registry_fingerprint(first) == calculate_registry_fingerprint(
        second
    )


def test_fingerprint_changes_with_real_content() -> None:
    empty = SourceRegistry(
        schema_version="1.0.0",
        registry_version="0.1.0",
        sources=[],
    )
    populated = SourceRegistry(
        schema_version="1.0.0",
        registry_version="0.1.0",
        sources=[make_source()],
    )
    assert calculate_registry_fingerprint(empty) != (
        calculate_registry_fingerprint(populated)
    )


def test_schema_generation_is_deterministic(tmp_path: Path) -> None:
    schema_path = tmp_path / "source_registry.schema.json"
    write_source_registry_schema(schema_path)
    first = schema_path.read_bytes()
    write_source_registry_schema(schema_path)
    assert schema_path.read_bytes() == first
    assert json.loads(first)["title"] == "SourceRegistry"


def test_loader_supports_explicit_windows_style_paths(tmp_path: Path) -> None:
    path = tmp_path / "sources.yaml"
    path.write_text(
        "schema_version: '1.0.0'\n"
        "registry_version: '0.1.0'\n"
        "sources: []\n",
        encoding="utf-8",
    )
    assert load_source_registry(Path(str(path))).sources == []


def test_loader_reports_missing_file_clearly(tmp_path: Path) -> None:
    with pytest.raises(SourceRegistryLoadError, match="file not found"):
        load_source_registry(tmp_path / "missing.yaml")


def test_duplicate_candidate_url_produces_warning_not_error() -> None:
    first = make_candidate(1, observed_url="https://example.com/shared")
    second = make_candidate(
        2,
        observed_url="HTTPS://EXAMPLE.COM:443/shared/#fragment",
    )
    result = validate_complete_source_context(
        make_context(candidates=[first, second])
    )
    assert result.status is ValidationStatus.PASSED_WITH_WARNINGS
    assert result.metrics["duplicate_count"] == 1


def test_complete_loader_integrates_asset_registry() -> None:
    context = load_complete_source_context(
        taxonomy_path=ROOT / "configs" / "taxonomy" / "source_taxonomy.yaml",
        candidates_path=ROOT
        / "configs"
        / "registries"
        / "source_candidates.yaml",
        sources_path=ROOT / "configs" / "registries" / "sources.yaml",
        investigation_path=ROOT
        / "configs"
        / "registries"
        / "source_investigation.yaml",
        asset_registry_path=ASSET_REGISTRY,
        asset_candidates_path=ASSET_CANDIDATES,
    )
    assert context.asset_registry.assets == []
    assert len(context.asset_candidates.candidates) == 8


def test_validation_cli_executes_without_network(tmp_path: Path) -> None:
    report = tmp_path / "report.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "validate_source_registry.py"),
            "--json-output",
            str(report),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Final status: PASSED" in completed.stdout
    assert json.loads(report.read_text(encoding="utf-8"))["status"] == "PASSED"
