"""UTF-8 YAML loaders for Source Registry and related Asset Registry files."""

from __future__ import annotations

from pathlib import Path
from typing import Any, TypeVar

import yaml
from pydantic import BaseModel, ValidationError

from tokenscope_dd.registry.loader import load_asset_candidates, load_asset_registry
from tokenscope_dd.source_registry.models import (
    CompleteSourceRegistryContext,
    SourceCandidateRegistry,
    SourceInvestigationRegistry,
    SourceRegistry,
    SourceTaxonomy,
)


SourceDocument = TypeVar("SourceDocument", bound=BaseModel)


class SourceRegistryLoadError(ValueError):
    """Raised when a Source Registry file cannot be read or validated."""


def _read_yaml(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    try:
        with file_path.open("r", encoding="utf-8") as stream:
            payload = yaml.safe_load(stream)
    except FileNotFoundError as exc:
        raise SourceRegistryLoadError(
            f"Source Registry file not found: {file_path}"
        ) from exc
    except OSError as exc:
        raise SourceRegistryLoadError(
            f"Cannot read Source Registry file {file_path}: {exc}"
        ) from exc
    except yaml.YAMLError as exc:
        raise SourceRegistryLoadError(
            f"Invalid YAML in Source Registry file {file_path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise SourceRegistryLoadError(
            f"Source Registry file {file_path} must contain a YAML mapping."
        )
    return payload


def _load_model(
    path: str | Path,
    model_type: type[SourceDocument],
) -> SourceDocument:
    file_path = Path(path)
    try:
        return model_type.model_validate(_read_yaml(file_path))
    except ValidationError as exc:
        raise SourceRegistryLoadError(
            f"Source Registry validation failed for {file_path}: {exc}"
        ) from exc


def load_source_taxonomy(path: str | Path) -> SourceTaxonomy:
    return _load_model(path, SourceTaxonomy)


def load_source_candidates(path: str | Path) -> SourceCandidateRegistry:
    return _load_model(path, SourceCandidateRegistry)


def load_source_registry(path: str | Path) -> SourceRegistry:
    return _load_model(path, SourceRegistry)


def load_source_investigation(
    path: str | Path,
) -> SourceInvestigationRegistry:
    return _load_model(path, SourceInvestigationRegistry)


def load_complete_source_context(
    *,
    taxonomy_path: str | Path,
    candidates_path: str | Path,
    sources_path: str | Path,
    investigation_path: str | Path,
    asset_registry_path: str | Path,
    asset_candidates_path: str | Path,
) -> CompleteSourceRegistryContext:
    """Load every document required for complete source validation."""

    try:
        asset_registry = load_asset_registry(asset_registry_path)
        asset_candidates = load_asset_candidates(asset_candidates_path)
    except ValueError as exc:
        raise SourceRegistryLoadError(
            f"Related Asset Registry could not be loaded: {exc}"
        ) from exc
    return CompleteSourceRegistryContext(
        taxonomy=load_source_taxonomy(taxonomy_path),
        candidates=load_source_candidates(candidates_path),
        sources=load_source_registry(sources_path),
        investigation=load_source_investigation(investigation_path),
        asset_registry=asset_registry,
        asset_candidates=asset_candidates,
    )
