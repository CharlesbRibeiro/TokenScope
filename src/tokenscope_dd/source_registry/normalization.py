"""Deterministic URL and locator normalization without network access."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import PureWindowsPath
from urllib.parse import SplitResult, urlsplit, urlunsplit


ALLOWED_URL_SCHEMES = frozenset({"http", "https"})


class SourceNormalizationError(ValueError):
    """Raised when a URL or locator cannot be normalized safely."""


def normalize_identity_text(value: str) -> str:
    """Normalize human-readable identity text only for comparison."""

    decomposed = unicodedata.normalize("NFKD", value.casefold().strip())
    without_marks = "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )
    simple_punctuation = re.sub(r"[\W_]+", " ", without_marks, flags=re.UNICODE)
    return " ".join(simple_punctuation.split())


def normalize_url(
    value: str,
    *,
    allowed_schemes: frozenset[str] = ALLOWED_URL_SCHEMES,
) -> str:
    """Return a comparison URL while preserving query parameters verbatim."""

    original = value.strip()
    if not original:
        raise SourceNormalizationError("URL cannot be empty.")

    try:
        parsed = urlsplit(original)
        port = parsed.port
    except ValueError as exc:
        raise SourceNormalizationError(f"Invalid URL {value!r}: {exc}") from exc

    scheme = parsed.scheme.casefold()
    if scheme not in allowed_schemes:
        raise SourceNormalizationError(
            f"URL scheme {parsed.scheme!r} is not allowed."
        )
    if parsed.hostname is None:
        raise SourceNormalizationError("URL must define a host.")
    if parsed.username is not None or parsed.password is not None:
        raise SourceNormalizationError(
            "Credentials must not be embedded in source URLs."
        )

    host = parsed.hostname.casefold()
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    default_port = (scheme == "http" and port == 80) or (
        scheme == "https" and port == 443
    )
    netloc = host if port is None or default_port else f"{host}:{port}"

    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/") or "/"

    normalized = SplitResult(
        scheme=scheme,
        netloc=netloc,
        path=path,
        query=parsed.query,
        fragment="",
    )
    return urlunsplit(normalized)


def normalize_locator(value: str) -> str:
    """Normalize a local locator deterministically for comparisons."""

    locator = value.strip()
    if not locator:
        raise SourceNormalizationError("Local locator cannot be empty.")
    if re.match(r"^[A-Za-z]:[\\/]", locator) or "\\" in locator:
        return str(PureWindowsPath(locator)).casefold()
    return re.sub(r"/+", "/", locator).rstrip("/").casefold()


def generate_source_candidate_id(
    observed_name: str,
    observed_url: str | None,
    observed_provider: str | None,
    discovered_in: str,
) -> str:
    """Generate a stable candidate ID independent of YAML ordering."""

    normalized_url = normalize_url(observed_url) if observed_url else ""
    identity = "|".join(
        (
            normalize_identity_text(discovered_in),
            normalize_identity_text(observed_name),
            normalize_identity_text(observed_provider or ""),
            normalized_url,
        )
    )
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]
    return f"ts_source_candidate_{digest}"


def generate_endpoint_id(
    source_id: str,
    *,
    url: str | None = None,
    locator: str | None = None,
) -> str:
    """Generate an endpoint ID from its source and normalized access identity."""

    if bool(url) == bool(locator):
        raise SourceNormalizationError(
            "Exactly one of url or locator is required to generate endpoint_id."
        )
    access_identity = normalize_url(url) if url else normalize_locator(locator or "")
    digest = hashlib.sha256(
        f"{source_id}|{access_identity}".encode("utf-8")
    ).hexdigest()[:12]
    return f"ts_endpoint_{digest}"
