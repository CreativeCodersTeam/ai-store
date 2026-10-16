#!/usr/bin/env python3
"""Run every dep-pr-cleanup unit test. Works with python3 / python / py -3 on any OS.

  python skills/tests/development/dep-pr-cleanup/scripts/run_tests.py [-v]
"""

import os
import sys
import unittest

sys.dont_write_bytecode = True  # no __pycache__ in the skill or plugin directory
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover(os.path.join(HERE, "unit"), top_level_dir=HERE)
    verbosity = 2 if "-v" in sys.argv[1:] else 1
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
