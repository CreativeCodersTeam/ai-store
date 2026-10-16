"""Run the GitHub CLI portably (Windows, macOS, Linux).

DEP_PR_CLEANUP_GH overrides the executable; a value ending in .py is run with the current
Python interpreter, which is how the test suite substitutes its mock.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from typing import List, Optional, Tuple


def gh_command() -> Optional[List[str]]:
    override = os.environ.get("DEP_PR_CLEANUP_GH")
    if override:
        return [sys.executable, override] if override.endswith(".py") else [override]
    found = shutil.which("gh")
    return [found] if found else None


def run_gh(args: List[str]) -> Tuple[int, str, str]:
    command = gh_command()
    if command is None:
        return 127, "", "gh not found on PATH"
    env = dict(os.environ)
    env.setdefault("GH_PROMPT_DISABLED", "1")
    env.setdefault("NO_COLOR", "1")
    try:
        completed = subprocess.run(command + args, capture_output=True, env=env)
    except OSError as error:
        return 127, "", "cannot run gh: %s" % error
    decode = lambda data: data.decode("utf-8", errors="replace")  # noqa: E731
    return completed.returncode, decode(completed.stdout), decode(completed.stderr)


def bot_key(login: Optional[str]) -> str:
    """Normalise `app/renovate`, `renovate[bot]`, and `renovate` to one key."""
    value = (login or "").strip().lower()
    if value.startswith("app/"):
        value = value[4:]
    if value.endswith("[bot]"):
        value = value[:-5]
    return value
