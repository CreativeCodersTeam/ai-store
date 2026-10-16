import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import helpers  # noqa: E402,F401

from deplib import versions as v  # noqa: E402


def rel(a, b, eco="npm", ha=None, hb=None):
    return v.compare(v.parse(a, eco, ha), v.parse(b, eco, hb))


class CompareTest(unittest.TestCase):
    def test_equal_exact_value(self):
        self.assertEqual(rel("4.17.21", "4.17.21"), v.EQUAL)
        self.assertEqual(rel("'4.17.21'", "4.17.21"), v.EQUAL)

    def test_newer_within_major(self):
        self.assertEqual(rel("4.18.0", "4.17.21"), v.NEWER)
        self.assertEqual(rel("^4.18.0", "^4.17.21"), v.NEWER)
        self.assertEqual(rel("4.17.21", "4.18.0"), v.OLDER)

    def test_newer_across_major(self):
        self.assertEqual(rel("5.0.0", "4.17.21"), v.NEWER_MAJOR)
        self.assertEqual(rel("v3", "v2.5.1", "github-actions"), v.NEWER_MAJOR)

    def test_short_versions_are_padded(self):
        self.assertEqual(rel("v4.1.0", "v4", "github-actions"), v.NEWER)
        self.assertEqual(rel("1.2", "1.2.0"), v.INCOMPARABLE)  # same release, different exact value

    def test_same_release_different_operator_is_not_equal(self):
        self.assertEqual(rel("^1.2.3", "1.2.3"), v.INCOMPARABLE)

    def test_prerelease_ordering(self):
        self.assertEqual(rel("2.0.0", "2.0.0-rc.1"), v.NEWER)
        self.assertEqual(rel("2.0.0-rc.2", "2.0.0-beta.5"), v.NEWER)
        self.assertEqual(rel("2.0.0-beta.1", "2.0.0"), v.OLDER)
        self.assertEqual(rel("2.0.0-weird", "2.0.0-odd"), v.INCOMPARABLE)

    def test_maven_qualifiers(self):
        self.assertEqual(rel("5.3.1.RELEASE", "5.3.0.RELEASE", "maven"), v.NEWER)
        self.assertEqual(rel("33.0.0-jre", "32.1.3-jre", "maven"), v.NEWER_MAJOR)
        self.assertEqual(rel("33.0.0-jre", "33.0.0-android", "maven"), v.INCOMPARABLE)

    def test_pep440_specifiers(self):
        self.assertEqual(rel(">=2.32.0,<3", ">=2.31.0,<3", "pypi"), v.NEWER)
        self.assertEqual(rel("==2.31.0", "==2.31.0", "pypi"), v.EQUAL)

    def test_npm_build_metadata_ignored_for_order(self):
        self.assertEqual(rel("1.1.8+spec-1.1.0", "1.1.7+spec-1.1.0"), v.NEWER)

    def test_docker_variant_must_match(self):
        self.assertEqual(rel("22-alpine", "20-alpine", "docker"), v.NEWER_MAJOR)
        self.assertEqual(rel("20.12-alpine", "20.11-alpine", "docker"), v.NEWER)
        self.assertEqual(rel("22", "20-alpine", "docker"), v.INCOMPARABLE)
        self.assertEqual(rel("20-alpine3.20", "20-alpine3.19", "docker"), v.INCOMPARABLE)

    def test_docker_digest_decides_equality(self):
        self.assertEqual(rel("20@sha256:aaa", "20@sha256:bbb", "docker", "20", "20"), v.INCOMPARABLE)
        self.assertEqual(rel("22@sha256:aaa", "20@sha256:bbb", "docker", "22", "20"), v.NEWER_MAJOR)
        self.assertEqual(rel("@sha256:aaa", "@sha256:bbb", "docker"), v.INCOMPARABLE)

    def test_sha_pins_use_the_version_comment(self):
        a, b = "a" * 40, "b" * 40
        self.assertEqual(rel(a, b, "github-actions", "v4.2.0", "v4.1.0"), v.NEWER)
        self.assertEqual(rel(a, b, "github-actions"), v.INCOMPARABLE)
        self.assertEqual(rel(a, a, "github-actions", "v4.2.0", "v4.2.0"), v.EQUAL)

    def test_non_versions_are_incomparable(self):
        self.assertEqual(rel("latest", "stable", "docker"), v.INCOMPARABLE)
        self.assertEqual(rel("npm:other@1.0.0", "1.0.0"), v.INCOMPARABLE)

    def test_major(self):
        self.assertEqual(v.parse("^4.17.21", "npm").major, 4)
        self.assertIsNone(v.parse("latest", "docker").major)


if __name__ == "__main__":
    unittest.main()
