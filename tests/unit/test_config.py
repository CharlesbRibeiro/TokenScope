"""Tests for repository-local path configuration."""

from tokenscope_dd import config


def test_repository_paths_are_derived_from_root() -> None:
    assert (config.REPOSITORY_ROOT / "pyproject.toml").is_file()
    assert config.DOCS_DIR == config.REPOSITORY_ROOT / "docs"
    assert config.RAW_DATA_DIR == config.REPOSITORY_ROOT / "data" / "raw"
    assert config.RUNS_DIR == config.REPOSITORY_ROOT / "outputs" / "runs"
    assert config.RISK_PASSPORTS_DIR == (
        config.REPOSITORY_ROOT / "outputs" / "risk_passports"
    )
