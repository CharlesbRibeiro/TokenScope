"""Unit and local integration tests for TS-004 Asset Registry."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tokenscope_dd.registry import (
    AssetCandidate,
    AssetRegistry,
    AssetTaxonomy,
    CandidateRegistry,
    CandidateStatus,
    CompleteRegistryContext,
    CoverageStatus,
    DeploymentStatus,
    EntityInvestigationRegistry,
    IdentityStatus,
    InvestigationStatus,
    NetworkDeployment,
    OfficialAsset,
    PossibleEntityType,
    RecordStatus,
    RegistryLoadError,
    RegistryPromotionError,
    ValidationStatus,
    calculate_registry_fingerprint,
    canonical_registry_json,
    generate_candidate_id,
    load_asset_candidates,
    load_asset_registry,
    load_asset_taxonomy,
    load_complete_registry_context,
    load_entity_investigation,
    normalize_identity_text,
    promote_candidate,
    validate_complete_registry,
    write_asset_registry_schema,
)
from tokenscope_dd.registry.models import AssetCategory, InvestigationEntity


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
FIXTURES_DIR = REPOSITORY_ROOT / "tests" / "fixtures" / "asset_registry"
OFFICIAL_CONFIGS = REPOSITORY_ROOT / "configs"
NOW = datetime(2026, 7, 23, 12, 0, tzinfo=timezone.utc)


def make_taxonomy() -> AssetTaxonomy:
    return AssetTaxonomy(
        schema_version="1.0.0",
        categories=[
            AssetCategory(
                category_id="tokenized_us_treasuries",
                display_name="Tokenized U.S. Treasuries",
                description="Test category.",
                active=True,
            ),
            AssetCategory(
                category_id="unclassified",
                display_name="Unclassified",
                description="Temporary test category.",
                active=True,
            ),
        ],
    )


def empty_candidates() -> CandidateRegistry:
    return CandidateRegistry(
        schema_version="1.0.0",
        candidate_registry_version="0.1.0",
        candidates=[],
    )


def empty_investigation() -> EntityInvestigationRegistry:
    return EntityInvestigationRegistry(
        schema_version="1.0.0",
        investigation_registry_version="0.1.0",
        entities=[],
    )


def make_asset(index: int = 1, **overrides: Any) -> OfficialAsset:
    payload: dict[str, Any] = {
        "asset_id": f"ts_asset_{index:012x}",
        "asset_key": f"asset_{index}",
        "official_name": f"Asset {index}",
        "short_name": None,
        "symbol": f"SYM{index}",
        "aliases": [],
        "category_id": "tokenized_us_treasuries",
        "subcategory_id": None,
        "product_type": None,
        "underlying_asset_type": None,
        "issuer_name": None,
        "issuer_legal_name": None,
        "issuer_reference": None,
        "jurisdictions": [],
        "official_website": None,
        "launch_date": None,
        "currency": None,
        "network_deployments": [],
        "record_status": RecordStatus.ACTIVE,
        "identity_status": IdentityStatus.UNVERIFIED,
        "coverage_status": CoverageStatus.NOT_STARTED,
        "source_refs": [],
        "identity_rationale": None,
        "schema_version": "1.0.0",
        "created_at": NOW,
        "updated_at": NOW,
        "last_verified_at": None,
        "registry_notes": None,
    }
    payload.update(overrides)
    return OfficialAsset.model_validate(payload)


def make_context(
    assets: list[OfficialAsset] | None = None,
    *,
    candidates: CandidateRegistry | None = None,
    investigation: EntityInvestigationRegistry | None = None,
    taxonomy: AssetTaxonomy | None = None,
) -> CompleteRegistryContext:
    return CompleteRegistryContext(
        taxonomy=taxonomy or make_taxonomy(),
        candidates=candidates or empty_candidates(),
        assets=AssetRegistry(
            schema_version="1.0.0",
            registry_version="0.1.0",
            assets=assets or [],
        ),
        investigation=investigation or empty_investigation(),
    )


def validate_assets(
    assets: list[OfficialAsset],
    **context_overrides: Any,
):
    return validate_complete_registry(
        make_context(assets, **context_overrides)
    )


def test_load_valid_taxonomy() -> None:
    taxonomy = load_asset_taxonomy(FIXTURES_DIR / "taxonomy_valid.yaml")
    assert {category.category_id for category in taxonomy.categories} == {
        "tokenized_us_treasuries",
        "unclassified",
    }


def test_load_empty_official_registry() -> None:
    registry = load_asset_registry(FIXTURES_DIR / "assets_empty.yaml")
    assert registry.registry_version == "0.1.0"
    assert registry.assets == []


def test_load_eight_historical_candidates_as_discovered() -> None:
    registry = load_asset_candidates(
        OFFICIAL_CONFIGS / "registries" / "asset_candidates.yaml"
    )
    assert len(registry.candidates) == 8
    assert {candidate.observed_name for candidate in registry.candidates} == {
        "BUIDL",
        "BENJI",
        "OUSG",
        "USDY",
        "USYC",
        "USTB",
        "STBT",
        "TBILL",
    }
    assert all(
        candidate.candidate_status is CandidateStatus.DISCOVERED
        and candidate.promoted_asset_id is None
        for candidate in registry.candidates
    )


def test_load_entities_under_investigation_outside_assets() -> None:
    registry = load_entity_investigation(
        OFFICIAL_CONFIGS / "registries" / "entity_investigation.yaml"
    )
    assert {entity.observed_name for entity in registry.entities} == {
        "Centrifuge",
        "Maple",
    }
    assert all(
        entity.possible_entity_type is PossibleEntityType.PLATFORM_OR_PROTOCOL
        and entity.investigation_status is InvestigationStatus.PENDING
        for entity in registry.entities
    )


def test_reject_duplicate_candidate_id() -> None:
    candidate = load_asset_candidates(
        FIXTURES_DIR / "candidates_valid.yaml"
    ).candidates[0]
    with pytest.raises(ValidationError, match="candidate_id values must be unique"):
        CandidateRegistry(
            schema_version="1.0.0",
            candidate_registry_version="0.1.0",
            candidates=[candidate, candidate.model_copy(deep=True)],
        )


def test_reject_duplicate_asset_id() -> None:
    first = make_asset(1)
    second = make_asset(2).model_copy(update={"asset_id": first.asset_id})
    with pytest.raises(ValidationError, match="asset_id values must be unique"):
        AssetRegistry(
            schema_version="1.0.0",
            registry_version="0.1.0",
            assets=[first, second],
        )


def test_asset_id_is_immutable_after_assignment() -> None:
    asset = make_asset(1)

    with pytest.raises(ValidationError, match="Field is frozen"):
        asset.asset_id = "ts_asset_000000000002"


def test_reject_duplicate_asset_key() -> None:
    first = make_asset(1)
    second = make_asset(2).model_copy(update={"asset_key": first.asset_key})
    with pytest.raises(ValidationError, match="asset_key values must be unique"):
        AssetRegistry(
            schema_version="1.0.0",
            registry_version="0.1.0",
            assets=[first, second],
        )


def test_repeated_symbol_is_accepted_with_warning() -> None:
    result = validate_assets(
        [make_asset(1, symbol="SAME"), make_asset(2, symbol="SAME")]
    )
    assert result.status is ValidationStatus.PASSED_WITH_WARNINGS
    assert result.errors == []
    assert any("symbols are not identity keys" in warning for warning in result.warnings)


def test_reject_unknown_category() -> None:
    result = validate_assets([make_asset(1, category_id="missing_category")])
    assert result.status is ValidationStatus.FAILED
    assert any("unknown category_id" in error for error in result.errors)


def test_accept_provisional_unclassified_asset() -> None:
    result = validate_assets(
        [
            make_asset(
                1,
                category_id="unclassified",
                identity_status=IdentityStatus.PROVISIONAL,
            )
        ]
    )
    assert result.status is ValidationStatus.PASSED


def test_reject_analysis_ready_unclassified_asset() -> None:
    result = validate_assets(
        [
            make_asset(
                1,
                category_id="unclassified",
                coverage_status=CoverageStatus.ANALYSIS_READY,
            )
        ]
    )
    assert result.status is ValidationStatus.FAILED
    assert any("cannot be ANALYSIS_READY" in error for error in result.errors)


def test_alias_normalization_is_unicode_and_punctuation_stable() -> None:
    assert normalize_identity_text("  Ásset---  ONE ") == "asset one"
    assert normalize_identity_text("asset_one") == "asset one"


def test_reject_duplicate_alias_inside_asset() -> None:
    result = validate_assets(
        [make_asset(1, aliases=["Ásset One", "asset-one"])]
    )
    assert result.status is ValidationStatus.FAILED
    assert any("duplicate aliases" in error for error in result.errors)


def test_reject_alias_conflict_between_assets() -> None:
    result = validate_assets(
        [
            make_asset(1, aliases=["Shared Identity"]),
            make_asset(2, official_name="shared-identity"),
        ]
    )
    assert result.status is ValidationStatus.FAILED
    assert any("conflicts between" in error for error in result.errors)


def test_all_required_state_values_are_available() -> None:
    assert {state.value for state in CandidateStatus} == {
        "DISCOVERED",
        "UNDER_REVIEW",
        "PROMOTED",
        "REJECTED",
        "DUPLICATE",
    }
    assert "ANALYSIS_READY" in {state.value for state in CoverageStatus}
    assert "VERIFIED" in {state.value for state in IdentityStatus}
    assert "ARCHIVED" in {state.value for state in RecordStatus}
    assert "DEPRECATED" in {state.value for state in DeploymentStatus}


def test_reject_invalid_candidate_state() -> None:
    payload = load_asset_candidates(
        FIXTURES_DIR / "candidates_valid.yaml"
    ).candidates[0].model_dump(mode="json")
    payload["candidate_status"] = "INVALID"
    with pytest.raises(ValidationError):
        AssetCandidate.model_validate(payload)


def test_reject_verified_without_sources() -> None:
    result = validate_assets(
        [
            make_asset(
                1,
                identity_status=IdentityStatus.VERIFIED,
                issuer_name="Issuer",
                identity_rationale="Confirmed from official references.",
                last_verified_at=NOW,
            )
        ]
    )
    assert any("needs source_refs" in error for error in result.errors)


def test_reject_verified_without_issuer() -> None:
    result = validate_assets(
        [
            make_asset(
                1,
                identity_status=IdentityStatus.VERIFIED,
                source_refs=["source:test"],
                identity_rationale="Confirmed from official references.",
                last_verified_at=NOW,
            )
        ]
    )
    assert any("identified issuer" in error for error in result.errors)


def test_reject_verified_without_identity_rationale() -> None:
    result = validate_assets(
        [
            make_asset(
                1,
                identity_status=IdentityStatus.VERIFIED,
                issuer_name="Issuer",
                source_refs=["source:test"],
                last_verified_at=NOW,
            )
        ]
    )
    assert any("identity_rationale" in error for error in result.errors)


def test_reject_contract_without_network() -> None:
    with pytest.raises(ValidationError):
        NetworkDeployment.model_validate(
            {
                "contract_address": "0x123",
                "deployment_status": "ACTIVE",
            }
        )


def test_empty_contract_is_normalized_to_none_and_chain_id_to_string() -> None:
    deployment = NetworkDeployment(
        network_name="Example Network",
        chain_id=1,
        contract_address=" ",
        deployment_status=DeploymentStatus.UNKNOWN,
    )
    assert deployment.chain_id == "1"
    assert deployment.contract_address is None


def test_reject_duplicate_contract_on_same_network() -> None:
    deployment = NetworkDeployment(
        network_name="Example",
        contract_address="0xABC",
        deployment_status=DeploymentStatus.ACTIVE,
    )
    result = validate_assets(
        [
            make_asset(
                1,
                network_deployments=[
                    deployment,
                    deployment.model_copy(deep=True),
                ],
            )
        ]
    )
    assert any("duplicates contract" in error for error in result.errors)


def test_reject_same_contract_across_assets() -> None:
    deployment = NetworkDeployment(
        network_name="Example",
        contract_address="0xABC",
        deployment_status=DeploymentStatus.ACTIVE,
    )
    result = validate_assets(
        [
            make_asset(1, network_deployments=[deployment]),
            make_asset(
                2,
                network_deployments=[deployment.model_copy(deep=True)],
            ),
        ]
    )
    assert any("conflicts between" in error for error in result.errors)


def test_promote_candidate_safely_without_mutating_inputs() -> None:
    candidates = load_asset_candidates(FIXTURES_DIR / "candidates_valid.yaml")
    assets = load_asset_registry(FIXTURES_DIR / "assets_empty.yaml")
    asset = make_asset(1)
    result = promote_candidate(
        candidate_id=candidates.candidates[0].candidate_id,
        asset=asset,
        taxonomy=make_taxonomy(),
        candidates=candidates,
        assets=assets,
        investigation=empty_investigation(),
    )
    assert candidates.candidates[0].candidate_status is CandidateStatus.DISCOVERED
    assert assets.assets == []
    assert result.candidates.candidates[0].candidate_status is CandidateStatus.PROMOTED
    assert result.candidates.candidates[0].promoted_asset_id == asset.asset_id
    assert result.assets.assets == [asset]


def test_failed_promotion_has_no_partial_change() -> None:
    candidates = load_asset_candidates(FIXTURES_DIR / "candidates_valid.yaml")
    assets = load_asset_registry(FIXTURES_DIR / "assets_empty.yaml")
    before_candidates = candidates.model_dump(mode="json")
    before_assets = assets.model_dump(mode="json")
    with pytest.raises(RegistryPromotionError, match="unknown category_id"):
        promote_candidate(
            candidate_id=candidates.candidates[0].candidate_id,
            asset=make_asset(1, category_id="missing_category"),
            taxonomy=make_taxonomy(),
            candidates=candidates,
            assets=assets,
            investigation=empty_investigation(),
        )
    assert candidates.model_dump(mode="json") == before_candidates
    assert assets.model_dump(mode="json") == before_assets


def test_rejected_candidate_is_preserved() -> None:
    original = load_asset_candidates(
        FIXTURES_DIR / "candidates_valid.yaml"
    ).candidates[0]
    rejected = original.model_copy(
        update={"candidate_status": CandidateStatus.REJECTED}
    )
    registry = CandidateRegistry(
        schema_version="1.0.0",
        candidate_registry_version="0.1.0",
        candidates=[rejected],
    )
    assert registry.candidates[0].candidate_status is CandidateStatus.REJECTED


def test_archived_asset_is_preserved_and_valid() -> None:
    asset = make_asset(1, record_status=RecordStatus.ARCHIVED)
    result = validate_assets([asset])
    assert result.status is ValidationStatus.PASSED
    assert make_context([asset]).assets.assets[0].record_status is RecordStatus.ARCHIVED


def test_canonical_serialization_ignores_alias_and_deployment_order() -> None:
    first = NetworkDeployment(
        network_name="Network B",
        chain_id="2",
        deployment_status=DeploymentStatus.ACTIVE,
    )
    second = NetworkDeployment(
        network_name="Network A",
        chain_id="1",
        deployment_status=DeploymentStatus.ACTIVE,
    )
    registry_a = AssetRegistry(
        schema_version="1.0.0",
        registry_version="0.1.0",
        assets=[
            make_asset(
                1,
                aliases=["Zulu", "Alpha"],
                network_deployments=[first, second],
            )
        ],
    )
    registry_b = AssetRegistry(
        schema_version="1.0.0",
        registry_version="0.1.0",
        assets=[
            make_asset(
                1,
                aliases=["Alpha", "Zulu"],
                network_deployments=[second, first],
            )
        ],
    )
    assert canonical_registry_json(registry_a) == canonical_registry_json(registry_b)


def test_fingerprint_equal_for_different_yaml_formatting(tmp_path: Path) -> None:
    compact = tmp_path / "compact.yaml"
    expanded = tmp_path / "expanded.yaml"
    compact.write_text(
        'schema_version: "1.0.0"\nregistry_version: "0.1.0"\nassets: []\n',
        encoding="utf-8",
    )
    expanded.write_text(
        "assets: [ ]\n\nregistry_version: '0.1.0'\nschema_version: '1.0.0'\n",
        encoding="utf-8",
    )
    assert calculate_registry_fingerprint(
        load_asset_registry(compact)
    ) == calculate_registry_fingerprint(load_asset_registry(expanded))


def test_fingerprint_changes_when_content_changes() -> None:
    empty = AssetRegistry(
        schema_version="1.0.0",
        registry_version="0.1.0",
        assets=[],
    )
    populated = AssetRegistry(
        schema_version="1.0.0",
        registry_version="0.1.0",
        assets=[make_asset(1)],
    )
    assert calculate_registry_fingerprint(empty) != calculate_registry_fingerprint(
        populated
    )


def test_empty_registry_fingerprint_is_stable_sha256() -> None:
    registry = load_asset_registry(FIXTURES_DIR / "assets_empty.yaml")
    first = calculate_registry_fingerprint(registry)
    second = calculate_registry_fingerprint(registry.model_copy(deep=True))
    assert first == second
    assert len(first) == 64


def test_json_schema_is_generated_from_pydantic_model(tmp_path: Path) -> None:
    schema_path = write_asset_registry_schema(tmp_path / "asset_registry.json")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["title"] == "AssetRegistry"
    assert "OfficialAsset" in schema["$defs"]
    assert set(schema["required"]) == {
        "schema_version",
        "registry_version",
        "assets",
    }


def test_platform_or_protocol_cannot_also_be_official_asset() -> None:
    investigation = EntityInvestigationRegistry(
        schema_version="1.0.0",
        investigation_registry_version="0.1.0",
        entities=[
            InvestigationEntity(
                observed_name="Centrifuge",
                possible_entity_type=PossibleEntityType.PLATFORM_OR_PROTOCOL,
                investigation_status=InvestigationStatus.PENDING,
                reason="Needs investigation.",
            )
        ],
    )
    result = validate_assets(
        [make_asset(1, official_name="Centrifuge")],
        investigation=investigation,
    )
    assert result.status is ValidationStatus.FAILED
    assert any("also registered as official asset" in error for error in result.errors)


def test_promoted_candidate_must_reference_existing_official_asset() -> None:
    discovered = load_asset_candidates(
        FIXTURES_DIR / "candidates_valid.yaml"
    ).candidates[0]
    promoted = AssetCandidate.model_validate(
        {
            **discovered.model_dump(mode="json"),
            "candidate_status": "PROMOTED",
            "promoted_asset_id": "ts_asset_000000000001",
        }
    )
    candidates = CandidateRegistry(
        schema_version="1.0.0",
        candidate_registry_version="0.1.0",
        candidates=[promoted],
    )
    result = validate_complete_registry(make_context(candidates=candidates))
    assert result.status is ValidationStatus.FAILED
    assert any("points to missing asset" in error for error in result.errors)


def test_candidate_id_is_stable_and_reproducible() -> None:
    expected = "ts_candidate_b2f03f4cd50b"
    assert generate_candidate_id(
        " BUIDL ",
        "buidl",
        "RWA_COLLECTION_20260709_020427",
    ) == expected


def test_loader_accepts_windows_path_string() -> None:
    windows_path = str(FIXTURES_DIR / "assets_empty.yaml")
    registry = load_asset_registry(windows_path)
    assert registry.assets == []


def test_complete_loader_uses_explicit_paths_independent_of_cwd(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    context = load_complete_registry_context(
        taxonomy_path=FIXTURES_DIR / "taxonomy_valid.yaml",
        candidates_path=FIXTURES_DIR / "candidates_valid.yaml",
        assets_path=FIXTURES_DIR / "assets_empty.yaml",
        investigation_path=FIXTURES_DIR / "investigation_valid.yaml",
    )
    assert len(context.candidates.candidates) == 1


def test_loader_reports_missing_file_clearly(tmp_path: Path) -> None:
    with pytest.raises(RegistryLoadError, match="Registry file not found"):
        load_asset_registry(tmp_path / "missing.yaml")


def test_validation_script_executes_without_internet() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(REPOSITORY_ROOT / "scripts" / "validate_asset_registry.py"),
        ],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Candidates: 8" in completed.stdout
    assert "Official assets: 0" in completed.stdout
    assert "Final status: PASSED" in completed.stdout
