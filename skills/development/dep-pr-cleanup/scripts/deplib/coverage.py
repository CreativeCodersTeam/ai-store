"""Decide which bot pull requests are obsolete.

A pull request is obsolete when every one of its dependency updates is covered by pull requests
that stay open. The rules (identity, relations, pair modes, the removal order) are documented in
references/coverage-rules.md - keep both in sync.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Tuple

from . import versions
from .manifests import Update

EXACT = "exact"  # only the same target value covers
NEWER = "newer"  # a newer target within the same major version covers too
ANY = "any"      # a newer target covers even across major versions
MODES = (EXACT, NEWER, ANY)


def default_mode(newer: bool, across_major: bool) -> str:
    if not newer:
        return EXACT
    return ANY if across_major else NEWER


def target(update: Update) -> versions.Version:
    return versions.parse(update.to_value, update.ecosystem, update.to_hint)


def relation(a: Update, b: Update) -> str:
    """How the target of update ``a`` relates to the target of update ``b`` (same identity)."""
    return versions.compare(target(a), target(b))


def covers(rel: str, mode: str) -> bool:
    if rel == versions.EQUAL:
        return True
    if rel == versions.NEWER:
        return mode in (NEWER, ANY)
    if rel == versions.NEWER_MAJOR:
        return mode == ANY
    return False


class Analysis:
    def __init__(self, prs: List[dict], newer: bool, across_major: bool,
                 overrides: Optional[Dict[Tuple[int, int], str]] = None):
        """``prs``: dicts with number, bot, base, evaluable, updates (List[Update])."""
        self.prs = {pr["number"]: pr for pr in prs}
        self.default = default_mode(newer, across_major)
        self.overrides = dict(overrides or {})

    # -- pair modes ---------------------------------------------------------------------------

    def mode(self, coverer: int, covered: int) -> str:
        return self.overrides.get((coverer, covered), self.default)

    def group_key(self, number: int) -> Tuple[str, str]:
        pr = self.prs[number]
        return (pr["bot"], pr["base"])

    # -- coverage -----------------------------------------------------------------------------

    def coverers_of(self, update: Update, covered: int, pool: Iterable[int]) -> List[Tuple[int, str]]:
        found = []
        for other in pool:
            mode = self.mode(other, covered)
            best = None
            for candidate in self.prs[other]["updates"]:
                if candidate.identity != update.identity:
                    continue
                rel = relation(candidate, update)
                if covers(rel, mode) and (best is None or rel == versions.EQUAL):
                    best = rel
            if best is not None:
                found.append((other, best))
        return found

    def fully_covered(self, number: int, pool: Iterable[int]) -> bool:
        pool = [p for p in pool if p != number]
        return all(self.coverers_of(u, number, pool) for u in self.prs[number]["updates"])

    def run(self) -> Dict[str, object]:
        evaluable = [n for n, pr in self.prs.items() if pr["evaluable"] and pr["updates"]]
        groups: Dict[Tuple[str, str], List[int]] = defaultdict(list)
        for number in sorted(evaluable):
            groups[self.group_key(number)].append(number)

        obsolete: Dict[int, List[int]] = {}
        for key, members in groups.items():
            kept = set(members)
            removed: List[int] = []
            changed = True
            while changed:
                changed = False
                # Smallest pull request first, oldest first among equals: the larger and newer
                # pull requests are the ones that stay open.
                for number in sorted(kept, key=lambda n: (len(self.prs[n]["updates"]), n)):
                    pool = kept - {number}
                    if not pool or not self.fully_covered(number, pool):
                        continue
                    # Removing it must not strip the coverage of an earlier removal (pair modes
                    # make coverage non-transitive).
                    if all(self.fully_covered(r, pool) for r in removed):
                        kept.discard(number)
                        removed.append(number)
                        changed = True
                        break
            for number in removed:
                obsolete[number] = sorted(kept)

        return {"groups": groups, "obsolete": obsolete}

    def explain(self, number: int, pool: Iterable[int]) -> List[dict]:
        """Per update of ``number``: the chosen coverer and the relation."""
        pool = [p for p in pool if p != number]
        details = []
        for update in self.prs[number]["updates"]:
            options = self.coverers_of(update, number, pool)
            options.sort(key=lambda item: (item[1] != versions.EQUAL, -len(self.prs[item[0]]["updates"]), -item[0]))
            details.append({
                "update": update,
                "coverers": options,
                "chosen": options[0] if options else None,
            })
        return details


def overlaps(prs: List[dict], analysis: Analysis) -> List[dict]:
    """Every pair of pull requests that update at least one common dependency identity."""
    result = []
    numbers = sorted(pr["number"] for pr in prs if pr["updates"])
    by_number = {pr["number"]: pr for pr in prs}
    for i, a in enumerate(numbers):
        for b in numbers[i + 1:]:
            pa, pb = by_number[a], by_number[b]
            shared = []
            for ua in pa["updates"]:
                for ub in pb["updates"]:
                    if ua.identity == ub.identity:
                        shared.append((ua, ub, relation(ua, ub)))
            if not shared:
                continue
            reason = None
            if pa["bot"] != pb["bot"]:
                reason = "different-bot"
            elif pa["base"] != pb["base"]:
                reason = "different-base"
            elif not (pa["evaluable"] and pb["evaluable"]):
                reason = "unevaluable"
            result.append({"a": a, "b": b, "shared": shared, "not_counted_reason": reason})
    return result
