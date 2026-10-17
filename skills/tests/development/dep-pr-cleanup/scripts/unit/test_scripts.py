"""End-to-end tests of collect_prs.py and analyze_prs.py against the mock gh."""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers import FIXTURES, file_diff, hunk, lockfile, npm, pr, run_script, write_scenario  # noqa: E402

MIXED = os.path.join(FIXTURES, "scenario-mixed")


class Workspace(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="dep-pr-cleanup-test-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def collect(self, scenario, *args, mode="", cwd=None):
        out = os.path.join(self.tmp, "collected.json")
        code, stdout, stderr = run_script("collect_prs.py", ["--repo", "acme/shop", "--output", out] + list(args),
                                          scenario, mode, cwd=cwd or self.tmp)
        data = None
        if code == 0:
            with open(out, encoding="utf-8") as handle:
                data = json.load(handle)
        return code, stdout, stderr, data, out

    def analyze(self, collected_path, *args):
        code, stdout, stderr = run_script("analyze_prs.py", ["--input", collected_path] + list(args))
        return code, (json.loads(stdout) if code == 0 else None), stderr


class CollectTest(Workspace):
    def scenario(self, entries):
        directory = os.path.join(self.tmp, "scenario")
        write_scenario(directory, entries)
        return directory

    def test_filters_bots_and_records_flags(self):
        human = pr(5, bot="someone")
        human["author"] = {"is_bot": False, "login": "someone"}
        scenario = self.scenario([
            (pr(1, body="👻 **Immortal**: This PR will be recreated if closed unmerged."), npm("package.json", ("a", "1", "2")),
             ["renovate[bot]", "alice"]),
            (pr(2, bot="dependabot", draft=True, mergeable="CONFLICTING", checks="FAILURE"), None, None),
            (pr(3, checks="PENDING"), npm("package.json", ("a", "1", "2")), None),
            (human, npm("package.json", ("a", "1", "2")), None),
            (pr(6, bot="my-renovate"), npm("package.json", ("a", "1", "2")), None),
        ])
        code, stdout, stderr, data, _ = self.collect(scenario)
        self.assertEqual(code, 0, stderr)
        summary = json.loads(stdout)
        self.assertEqual(summary["bot_prs"], 3)
        self.assertEqual(summary["other_open_prs"], 2)
        self.assertEqual(summary["diff_errors"], [2])
        by = {p["number"]: p for p in data["prs"]}
        self.assertEqual(sorted(by), [1, 2, 3])
        self.assertTrue(by[1]["immortal"])
        self.assertEqual(by[1]["non_bot_commit_authors"], ["alice"])
        self.assertEqual((by[2]["bot"], by[2]["is_draft"], by[2]["mergeable"], by[2]["checks"]),
                         ("dependabot", True, "CONFLICTING", "failure"))
        self.assertIn("exceeded", by[2]["diff_error"])
        self.assertEqual(by[3]["checks"], "pending")
        self.assertEqual([b["login"] for b in data["bots"]], ["dependabot", "renovate"])

    def test_extra_bots_from_argument_and_config(self):
        scenario = self.scenario([(pr(6, bot="my-renovate"), npm("package.json", ("a", "1", "2")), None),
                                  (pr(7, bot="snyk-bot"), npm("package.json", ("a", "1", "2")), None)])
        config = os.path.join(self.tmp, "cfg.json")
        with open(config, "w", encoding="utf-8") as handle:
            json.dump({"bots": ["snyk-bot"], "acrossMajor": True}, handle)
        code, stdout, stderr, data, _ = self.collect(scenario, "--bot", "app/my-renovate", "--config", config)
        self.assertEqual(code, 0, stderr)
        self.assertEqual([p["number"] for p in data["prs"]], [6, 7])
        sources = {b["login"]: b["source"] for b in data["bots"]}
        self.assertEqual(sources, {"dependabot": "default", "renovate": "default", "snyk-bot": "config",
                                   "my-renovate": "argument"})
        self.assertEqual(data["config"]["values"], {"bots": ["snyk-bot"], "acrossMajor": True})

    def test_config_is_found_in_the_repository_and_can_drop_defaults(self):
        repo = os.path.join(self.tmp, "repo")
        os.makedirs(os.path.join(repo, ".github"))
        with open(os.path.join(repo, ".github", "dep-pr-cleanup.json"), "w", encoding="utf-8") as handle:
            json.dump({"includeDefaultBots": False, "bots": ["my-renovate[bot]"]}, handle)
        scenario = self.scenario([(pr(1), npm("package.json", ("a", "1", "2")), None),
                                  (pr(6, bot="my-renovate"), npm("package.json", ("a", "1", "2")), None)])
        code, _, stderr, data, _ = self.collect(scenario, cwd=repo)
        self.assertEqual(code, 0, stderr)
        self.assertEqual([p["number"] for p in data["prs"]], [6])

    def test_exit_codes(self):
        scenario = self.scenario([(pr(1), npm("package.json", ("a", "1", "2")), None)])
        self.assertEqual(self.collect(scenario, mode="unauth")[0], 2)
        self.assertEqual(self.collect(scenario, mode="no-repo")[0], 3)
        self.assertEqual(self.collect(scenario, mode="list-fails")[0], 3)
        self.assertEqual(self.collect(scenario, "--limit", "0")[0], 1)
        self.assertEqual(self.collect(scenario, "--no-default-bots")[0], 1)
        bad = os.path.join(self.tmp, "bad.json")
        with open(bad, "w", encoding="utf-8") as handle:
            handle.write('{"bots": "renovate"}')
        self.assertEqual(self.collect(scenario, "--config", bad)[0], 4)
        with open(bad, "w", encoding="utf-8") as handle:
            handle.write('{"unknown": 1}')
        self.assertEqual(self.collect(scenario, "--config", bad)[0], 4)
        self.assertEqual(self.collect(scenario, "--config", os.path.join(self.tmp, "missing.json"))[0], 4)

    def test_gh_missing(self):
        out = os.path.join(self.tmp, "c.json")
        code, _, stderr = run_script("collect_prs.py", ["--output", out], env_extra={
            "DEP_PR_CLEANUP_GH": os.path.join(self.tmp, "no-such-gh")})
        self.assertEqual(code, 2, stderr)

    def test_truncation_is_reported(self):
        scenario = self.scenario([(pr(n), npm("package.json", ("a", "1", "2")), None) for n in (1, 2, 3)])
        code, stdout, _, _, _ = self.collect(scenario, "--limit", "2")
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(stdout)["truncated"])


class AnalyzeMixedTest(Workspace):
    """scenario-mixed: see ../README.md for the intended outcome of every pull request."""

    def run_mixed(self, *args):
        code, _, stderr, _, path = self.collect(MIXED)
        self.assertEqual(code, 0, stderr)
        code, result, stderr = self.analyze(path, *args)
        self.assertEqual(code, 0, stderr)
        return result

    @staticmethod
    def statuses(result):
        return {p["number"]: p["status"] for p in result["prs"]}

    def test_defaults(self):
        result = self.run_mixed()
        status = self.statuses(result)
        self.assertEqual({n for n, s in status.items() if s == "obsolete"}, {101, 104, 111})
        self.assertEqual({n for n, s in status.items() if s == "unevaluable"}, {107, 108})
        proposals = {p["number"]: p for p in result["proposals"]}
        self.assertEqual(proposals[101]["covered_by"], [102])
        self.assertEqual(proposals[104]["covered_by"], [109])
        self.assertEqual(proposals[111]["covered_by"], [112, 113])
        self.assertTrue(any("alice" in w for w in proposals[101]["warnings"]))
        self.assertTrue(any("failing checks" in w for w in proposals[101]["warnings"]))
        self.assertTrue(any("immortal" in w for w in proposals[104]["warnings"]))
        self.assertEqual(result["options"]["default_mode"], "newer")

    def test_overlaps_are_listed_with_reasons(self):
        result = self.run_mixed()
        pairs = {(o["a"], o["b"]): o for o in result["overlaps"]}
        self.assertEqual(pairs[(101, 105)]["not_counted_reason"], "different-bot")
        self.assertEqual(pairs[(101, 106)]["not_counted_reason"], "different-base")
        self.assertTrue(pairs[(101, 102)]["counted"])
        major = [s for s in pairs[(102, 103)]["shared"] if s["name"] == "lodash"][0]
        self.assertEqual(major["relation"], "b-newer-major")
        toggles = {(t["coverer"], t["covered"]): t for t in result["pair_toggles"]}
        self.assertEqual(toggles[(103, 102)]["newer_major_updates"], 1)
        self.assertEqual(toggles[(103, 102)]["mode"], "newer")
        self.assertEqual((toggles[(103, 102)]["counts_now"], toggles[(103, 102)]["switch_to"]), ("none", "any"))
        self.assertEqual((toggles[(112, 111)]["counts_now"], toggles[(112, 111)]["switch_to"]), ("all", "exact"))

    def test_across_major(self):
        status = self.statuses(self.run_mixed("--across-major", "yes"))
        self.assertEqual({n for n, s in status.items() if s == "obsolete"}, {101, 102, 104, 111})

    def test_exact_only(self):
        status = self.statuses(self.run_mixed("--newer", "no"))
        self.assertEqual({n for n, s in status.items() if s == "obsolete"}, {101, 104})

    def test_pair_mode_override(self):
        result = self.run_mixed("--across-major", "yes", "--pair-mode", "109:102=exact")
        status = self.statuses(result)
        self.assertEqual(status[102], "kept")
        self.assertEqual(result["options"]["pair_modes"], [{"coverer": 109, "covered": 102, "mode": "exact"}])

    def test_usage_errors(self):
        code, _, _, _, path = self.collect(MIXED)
        self.assertEqual(self.analyze(path, "--pair-mode", "109-102")[0], 1)
        self.assertEqual(self.analyze(path, "--pair-mode", "999:102=exact")[0], 1)
        self.assertEqual(self.analyze(path, "--newer", "maybe")[0], 1)
        broken = os.path.join(self.tmp, "broken.json")
        with open(broken, "w", encoding="utf-8") as handle:
            handle.write("{not json")
        self.assertEqual(self.analyze(broken)[0], 3)
        self.assertEqual(self.analyze(os.path.join(self.tmp, "missing.json"))[0], 3)


class AnalyzeEdgeTest(Workspace):
    def test_no_bot_pull_requests(self):
        directory = os.path.join(self.tmp, "empty")
        write_scenario(directory, [])
        code, _, stderr, _, path = self.collect(directory)
        self.assertEqual(code, 0, stderr)
        code, result, _ = self.analyze(path)
        self.assertEqual(code, 0)
        self.assertEqual(result["summary"]["bot_prs"], 0)
        self.assertEqual(result["proposals"], [])

    def test_lockfile_only_pull_request_is_unevaluable(self):
        directory = os.path.join(self.tmp, "lock")
        write_scenario(directory, [(pr(1), lockfile(), None), (pr(2), npm("package.json", ("a", "1.0.0", "1.1.0")) + lockfile(), None)])
        _, _, _, _, path = self.collect(directory)
        _, result, _ = self.analyze(path)
        by = {p["number"]: p for p in result["prs"]}
        self.assertEqual(by[1]["status"], "unevaluable")
        self.assertEqual(by[2]["status"], "kept")
        self.assertEqual(by[2]["ignored_lockfiles"], ["package-lock.json"])

    def test_renovate_major_title_warning(self):
        directory = os.path.join(self.tmp, "major")
        write_scenario(directory, [
            (pr(1, title="Update dependency eslint to v9"), npm("package.json", ("eslint", "9.0.0", "9.1.0")), None),
            (pr(2, title="Update dependency eslint to v9.2.0"), npm("package.json", ("eslint", "9.0.0", "9.2.0")), None)])
        _, _, _, _, path = self.collect(directory)
        _, result, _ = self.analyze(path)
        self.assertEqual([p["number"] for p in result["proposals"]], [1])
        self.assertTrue(any("ignore every future update" in w for w in result["proposals"][0]["warnings"]))


if __name__ == "__main__":
    unittest.main()
