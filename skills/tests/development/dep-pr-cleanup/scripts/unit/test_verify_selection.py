import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers import FIXTURES, run_script  # noqa: E402

MIXED = os.path.join(FIXTURES, "scenario-mixed")


class VerifySelectionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="dep-pr-cleanup-verify-")
        self.before = self.analysis(MIXED, "before")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def analysis(self, scenario, name):
        collected = os.path.join(self.tmp, name + "-collected.json")
        result = os.path.join(self.tmp, name + ".json")
        code, _, err = run_script("collect_prs.py", ["--repo", "acme/shop", "--output", collected], scenario)
        self.assertEqual(code, 0, err)
        code, _, err = run_script("analyze_prs.py", ["--input", collected, "--output", result])
        self.assertEqual(code, 0, err)
        return result

    def verify(self, after, select):
        code, out, err = run_script("verify_selection.py", ["--before", self.before, "--after", after, "--select", select])
        return code, (json.loads(out) if out.strip() else None), err

    def changed_scenario(self, mutate):
        directory = os.path.join(self.tmp, "changed")
        shutil.copytree(MIXED, directory)
        path = os.path.join(directory, "prs.json")
        with open(path, encoding="utf-8") as handle:
            prs = json.load(handle)
        prs = mutate(prs)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(prs, handle)
        return directory

    def test_unchanged_is_safe(self):
        code, result, _ = self.verify(self.analysis(MIXED, "after"), "101,#104")
        self.assertEqual(code, 0)
        self.assertEqual(result, {"safe": [101, 104], "changed": []})

    def test_new_commit_on_coverer_blocks(self):
        def mutate(prs):
            for item in prs:
                if item["number"] == 102:
                    item["headRefOid"] = "f" * 40
            return prs
        code, result, _ = self.verify(self.analysis(self.changed_scenario(mutate), "after"), "101,104")
        self.assertEqual(code, 4)
        self.assertEqual(result["safe"], [104])
        self.assertIn("covering #102 has new commits", result["changed"][0]["reasons"])

    def test_closed_pull_request_blocks(self):
        mutate = lambda prs: [p for p in prs if p["number"] != 109]  # noqa: E731
        code, result, _ = self.verify(self.analysis(self.changed_scenario(mutate), "after"), "104")
        self.assertEqual(code, 4)
        reasons = result["changed"][0]["reasons"]
        self.assertIn("covering #109 is no longer open", reasons)
        self.assertTrue(any("no longer proposed" in r for r in reasons))

    def test_usage(self):
        after = self.analysis(MIXED, "after")
        self.assertEqual(self.verify(after, "102")[0], 1)  # 102 was never proposed
        self.assertEqual(self.verify(after, "abc")[0], 1)
        self.assertEqual(self.verify(os.path.join(self.tmp, "missing.json"), "101")[0], 3)


if __name__ == "__main__":
    unittest.main()
