"""Central project paths derived from the repository root."""

from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

DOCS_DIR = REPOSITORY_ROOT / "docs"
CONFIGS_DIR = REPOSITORY_ROOT / "configs"

DATA_DIR = REPOSITORY_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

OUTPUTS_DIR = REPOSITORY_ROOT / "outputs"
RUNS_DIR = OUTPUTS_DIR / "runs"
REPORTS_DIR = OUTPUTS_DIR / "reports"
RISK_PASSPORTS_DIR = OUTPUTS_DIR / "risk_passports"

LOGS_DIR = REPOSITORY_ROOT / "logs"
