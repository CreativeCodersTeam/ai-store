"""Version values of dependency updates and how two target versions relate.

A target version has three facets:

* ``exact``   - the normalised raw value; two updates reach the same target only if these match.
* ``release`` - the numeric release tuple used for ordering (``None`` if not comparable).
* ``suffix``  - pre-release / qualifier / variant text after the release.

See references/coverage-rules.md for the rules implemented here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Tuple

_SHA = re.compile(r"^[0-9a-f]{40}$")
_LEADING_OPERATORS = re.compile(r"^[\s=<>!~^*v]+", re.IGNORECASE)
_VERSION = re.compile(r"(?P<release>\d+(?:\.\d+)*)(?P<suffix>[-+._]?[0-9A-Za-z][0-9A-Za-z.+_-]*)?")

# Ordering of well-known pre-release and qualifier words (semver, PEP 440, Maven, NuGet).
_QUALIFIER_RANK = {
    "dev": 0, "snapshot": 0, "nightly": 0,
    "alpha": 1, "a": 1, "preview": 1, "pre": 1,
    "beta": 2, "b": 2,
    "milestone": 3, "m": 3,
    "rc": 4, "cr": 4,
    "": 5, "final": 5, "ga": 5, "release": 5,
    "post": 6, "sp": 6,
}

EQUAL = "equal"
NEWER = "newer"            # a is newer than b within the same major version
NEWER_MAJOR = "newer-major"  # a is newer than b and crosses a major version
OLDER = "older"
INCOMPARABLE = "incomparable"


@dataclass(frozen=True)
class Version:
    exact: str
    release: Optional[Tuple[int, ...]]
    suffix: str
    variant_sensitive: bool  # Docker tags: the suffix is a variant and must match

    @property
    def major(self) -> Optional[int]:
        return self.release[0] if self.release else None

    def display(self) -> str:
        return self.exact


def normalise(raw: str) -> str:
    return raw.strip().strip("\"'").strip()


def parse(raw: str, ecosystem: str, comparable_hint: Optional[str] = None) -> Version:
    """Parse a target value.

    ``comparable_hint`` is the human-readable version that stands behind an opaque value,
    for example the ``# v4.1.0`` comment of a SHA-pinned action. The opaque value still
    decides equality; the hint only makes the value orderable.
    """
    exact = normalise(raw)
    source = comparable_hint if comparable_hint is not None else exact
    variant_sensitive = ecosystem == "docker"
    if comparable_hint is None and (_SHA.match(exact) or exact.startswith("sha256:")):
        return Version(exact, None, "", variant_sensitive)
    if "@sha256:" in source:
        source = source.split("@", 1)[0]
    if ecosystem in ("npm", "nuget"):
        source = source.split("+", 1)[0]  # build metadata does not take part in ordering
    stripped = _LEADING_OPERATORS.sub("", source)
    match = _VERSION.match(stripped)
    if not match:
        return Version(exact, None, "", variant_sensitive)
    release = tuple(int(part) for part in match.group("release").split("."))
    suffix = (match.group("suffix") or "").lstrip("-+._")
    return Version(exact, release, suffix, variant_sensitive)


def _padded(a: Tuple[int, ...], b: Tuple[int, ...]) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
    width = max(len(a), len(b))
    return a + (0,) * (width - len(a)), b + (0,) * (width - len(b))


def _qualifier_key(suffix: str) -> Optional[Tuple[int, Tuple[int, ...]]]:
    if suffix == "":
        return (_QUALIFIER_RANK[""], ())
    match = re.match(r"^([A-Za-z]*)[.-]?(\d+(?:\.\d+)*)?$", suffix)
    if not match:
        return None
    word = match.group(1).lower()
    if word not in _QUALIFIER_RANK:
        return None
    numbers = tuple(int(n) for n in (match.group(2) or "").split(".") if n)
    return (_QUALIFIER_RANK[word], numbers)


def compare(a: Version, b: Version) -> str:
    """Relation of target ``a`` to target ``b``."""
    if a.exact == b.exact:
        return EQUAL
    if a.release is None or b.release is None:
        return INCOMPARABLE
    if a.variant_sensitive and a.suffix != b.suffix:
        return INCOMPARABLE
    ra, rb = _padded(a.release, b.release)
    if ra == rb:
        if a.variant_sensitive or a.suffix == b.suffix:
            # Same orderable version, different exact value (another digest, SHA, or range
            # operator): the two targets are not the same content and neither is newer.
            return INCOMPARABLE
        qa, qb = _qualifier_key(a.suffix), _qualifier_key(b.suffix)
        if qa is None or qb is None or qa == qb:
            return INCOMPARABLE
        return NEWER if qa > qb else OLDER
    if ra < rb:
        return OLDER
    return NEWER_MAJOR if a.major != b.major else NEWER
