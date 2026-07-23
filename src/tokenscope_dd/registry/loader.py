"""UTF-8 YAML loaders for Asset Registry documents."""

from __future__ import annotations

from pathlib import Path
from typing import Any, TypeVar

import yaml
from pydantic import BaseModel, ValidationError

from tokenscope_dd.registry.models import (
    AssetRegistry,
    AssetTaxonomy,
    CandidateRegistry,
    CompleteRegistryContext,
    EntityInvestigationRegistry,
)


RegistryDocument = TypeVar("RegistryDocument", bound=BaseModel)


class RegistryLoadError(ValueError):
    """Raised when a registry file cannot be read or validated."""


def _read_yaml(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    try:
        with file_path.open("r", encoding="utf-8") as stream:
            payload = yaml.safe_load(stream)
    except FileNotFoundError as exc:
        raise RegistryLoadError(f"Registry file not found: {file_path}") from exc
    except OSError as exc:
        raise RegistryLoadError(f"Cannot read registry file {file_path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise RegistryLoadError(f"Invalid YAML in {file_path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise RegistryLoadError(
            f"Registry file {file_path} must contain a YAML mapping."
        )
    return payload


def _load_model(
    path: str | Path,
    model_type: type[RegistryDocument],
) -> RegistryDocument:
    file_path = Path(path)
    try:
        return model_type.model_validate(_read_yaml(file_path))
    except ValidationError as exc:
        raise RegistryLoadError(
            f"Registry validation failed for {file_path}: {exc}"
        ) from exc


def load_asset_taxonomy(path: str | Path) -> AssetTaxonomy:
    """Load and validate an asset category taxonomy."""

    return _load_model(path, AssetTaxonomy)


def load_asset_candidates(path: str | Path) -> CandidateRegistry:
    """Load and validate candidate observations."""

    return _load_model(path, CandidateRegistry)


def load_asset_registry(path: str | Path) -> AssetRegistry:
    """Load and validate the official Asset Registry."""

    return _load_model(path, AssetRegistry)


def load_entity_investigation(
    path: str | Path,
) -> EntityInvestigationRegistry:
    """Load and validate entities kept outside the official registry."""

    return _load_model(path, EntityInvestigationRegistry)


def load_complete_registry_context(
    *,
    taxonomy_path: str | Path,
    candidates_path: str | Path,
    assets_path: str | Path,
    investigation_path: str | Path,
) -> CompleteRegistryContext:
    """Load every registry document required for complete validation."""

    return CompleteRegistryContext(
        taxonomy=load_asset_taxonomy(taxonomy_path),
        candidates=load_asset_candidates(candidates_path),
        assets=load_asset_registry(assets_path),
        investigation=load_entity_investigation(investigation_path),
    )
