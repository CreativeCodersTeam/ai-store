import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import helpers  # noqa: E402,F401

from deplib.coverage import Analysis  # noqa: E402
from deplib.manifests import Update  # noqa: E402


def u(name, to, path="package.json", eco="npm"):
    return Update(eco, name, path, "0.0.1", to)


def pr(number, *updates, bot="renovate", base="main", evaluable=True):
    return {"number": number, "bot": bot, "base": base, "evaluable": evaluable, "updates": list(updates)}


def obsolete(prs, newer=True, across_major=False, overrides=None):
    return Analysis(prs, newer, across_major, overrides).run()["obsolete"]


class CoverageTest(unittest.TestCase):
    def test_subset_with_same_versions_is_obsolete(self):
        result = obsolete([pr(1, u("a", "1.1.0")), pr(2, u("a", "1.1.0"), u("b", "2.0.1"))])
        self.assertEqual(result, {1: [2]})

    def test_identical_pull_requests_keep_the_newest(self):
        result = obsolete([pr(7, u("a", "1.1.0")), pr(3, u("a", "1.1.0"))])
        self.assertEqual(result, {3: [7]})

    def test_newer_version_counts_only_when_enabled(self):
        prs = [pr(1, u("a", "1.1.0")), pr(2, u("a", "1.2.0"))]
        self.assertEqual(obsolete(prs), {1: [2]})
        self.assertEqual(obsolete(prs, newer=False), {})

    def test_older_version_never_covers(self):
        self.assertEqual(obsolete([pr(1, u("a", "1.2.0")), pr(2, u("a", "1.1.0"), u("b", "1.0.0"))]), {})

    def test_major_boundary_needs_its_own_option(self):
        # The Renovate minor/major pair: a -> 2.5.0 and a -> 3.0.0
        prs = [pr(1, u("a", "2.5.0")), pr(2, u("a", "3.0.0"))]
        self.assertEqual(obsolete(prs), {})
        self.assertEqual(obsolete(prs, across_major=True), {1: [2]})
        self.assertEqual(obsolete(prs, newer=False, across_major=True), {})

    def test_union_of_several_pull_requests_covers(self):
        prs = [pr(1, u("a", "1.1.0"), u("b", "1.1.0")), pr(2, u("a", "1.2.0")), pr(3, u("b", "1.2.0"))]
        self.assertEqual(obsolete(prs), {1: [2, 3]})

    def test_partially_covered_stays(self):
        prs = [pr(1, u("a", "1.1.0"), u("c", "1.0.0")), pr(2, u("a", "1.2.0"))]
        self.assertEqual(obsolete(prs), {})

    def test_path_is_part_of_the_identity(self):
        prs = [pr(1, u("a", "1.1.0", path="web/package.json")), pr(2, u("a", "1.1.0", path="api/package.json"))]
        self.assertEqual(obsolete(prs), {})

    def test_different_bot_or_base_never_covers(self):
        self.assertEqual(obsolete([pr(1, u("a", "1.1.0"), bot="dependabot"), pr(2, u("a", "1.1.0"))]), {})
        self.assertEqual(obsolete([pr(1, u("a", "1.1.0"), base="release/1.x"), pr(2, u("a", "1.1.0"))]), {})

    def test_unevaluable_pull_request_neither_covers_nor_is_covered(self):
        self.assertEqual(obsolete([pr(1, u("a", "1.1.0")), pr(2, u("a", "1.1.0"), evaluable=False)]), {})
        self.assertEqual(obsolete([pr(1, u("a", "1.1.0"), evaluable=False), pr(2, u("a", "1.1.0"))]), {})

    def test_covering_pull_requests_are_never_obsolete_themselves(self):
        # Chain 1 -> 2 -> 3 (newer each time): everything collapses onto the newest.
        prs = [pr(1, u("a", "1.1.0")), pr(2, u("a", "1.2.0")), pr(3, u("a", "1.3.0"))]
        result = obsolete(prs)
        self.assertEqual(result, {1: [3], 2: [3]})
        for covered_by in result.values():
            self.assertTrue(set(covered_by).isdisjoint(result))

    def test_pair_override_breaks_transitivity_safely(self):
        # 3 may not replace 1 (exact only), so 2 must stay open as the cover of 1.
        prs = [pr(1, u("a", "1.0.0")), pr(2, u("a", "1.1.0")), pr(3, u("a", "1.2.0"))]
        result = obsolete(prs, overrides={(3, 1): "exact"})
        self.assertEqual(sorted(result), [1])
        self.assertEqual(result[1], [2, 3])

    def test_pair_override_can_allow_a_major_replacement(self):
        prs = [pr(1, u("a", "2.5.0")), pr(2, u("a", "3.0.0"))]
        self.assertEqual(obsolete(prs, overrides={(2, 1): "any"}), {1: [2]})

    def test_explain_prefers_equal_and_larger_cover(self):
        prs = [pr(1, u("a", "1.1.0")), pr(2, u("a", "1.2.0")), pr(3, u("a", "1.1.0"), u("b", "1.0.0"))]
        analysis = Analysis(prs, True, False)
        result = analysis.run()["obsolete"]
        self.assertEqual(sorted(result), [1])
        detail = analysis.explain(1, result[1])[0]
        self.assertEqual(detail["chosen"], (3, "equal"))
        self.assertEqual(sorted(c for c, _ in detail["coverers"]), [2, 3])


if __name__ == "__main__":
    unittest.main()
