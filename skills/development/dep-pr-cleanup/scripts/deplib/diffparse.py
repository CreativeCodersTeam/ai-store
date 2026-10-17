"""Parse the unified diff that `gh pr diff` prints into files, hunks, and lines."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

_DIFF_GIT = re.compile(r"^diff --git a/(.*) b/(.*)$")
_HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@")


@dataclass
class DiffFile:
    old_path: Optional[str]
    new_path: Optional[str]
    binary: bool = False
    # Each hunk is a list of (tag, text) with tag in {" ", "-", "+"}.
    hunks: List[List[Tuple[str, str]]] = field(default_factory=list)

    @property
    def path(self) -> str:
        return self.new_path or self.old_path or ""

    @property
    def status(self) -> str:
        if self.binary:
            return "binary"
        if self.old_path is None:
            return "added"
        if self.new_path is None:
            return "deleted"
        if self.old_path != self.new_path:
            return "renamed"
        return "modified"


def _strip_prefix(value: str, prefix: str) -> Optional[str]:
    value = value.split("\t", 1)[0]
    if value == "/dev/null":
        return None
    return value[len(prefix):] if value.startswith(prefix) else value


def parse_diff(text: str) -> List[DiffFile]:
    """Split a multi-file unified diff. CRLF line endings are tolerated."""
    files: List[DiffFile] = []
    current: Optional[DiffFile] = None
    hunk: Optional[List[Tuple[str, str]]] = None

    for raw in text.splitlines():
        line = raw.rstrip("\r")
        match = _DIFF_GIT.match(line)
        if match:
            current = DiffFile(old_path=match.group(1), new_path=match.group(2))
            files.append(current)
            hunk = None
            continue
        if current is None:
            continue
        if hunk is None:
            # File header region.
            if line.startswith("--- "):
                current.old_path = _strip_prefix(line[4:], "a/")
            elif line.startswith("+++ "):
                current.new_path = _strip_prefix(line[4:], "b/")
            elif line.startswith("new file mode"):
                current.old_path = None
            elif line.startswith("deleted file mode"):
                current.new_path = None
            elif line.startswith("Binary files ") or line.startswith("GIT binary patch"):
                current.binary = True
            elif _HUNK.match(line):
                hunk = []
                current.hunks.append(hunk)
            continue
        if _HUNK.match(line):
            hunk = []
            current.hunks.append(hunk)
        elif line.startswith("\\"):
            continue  # "\ No newline at end of file"
        elif line[:1] in (" ", "-", "+"):
            hunk.append((line[0], line[1:]))
        elif line == "":
            hunk.append((" ", ""))
        else:
            hunk = None  # unexpected text ends the hunk; next header follows
    return files


@dataclass
class ChangeBlock:
    """A run of consecutive removed/added lines inside one hunk."""

    removed: List[Tuple[str, List[str]]]  # (text, preceding lines in the old file view)
    added: List[Tuple[str, List[str]]]  # (text, preceding lines in the new file view)


def change_blocks(hunk: List[Tuple[str, str]]) -> List[ChangeBlock]:
    """Group a hunk into change blocks; each changed line carries its preceding context.

    The context of a removed line is every earlier line of the hunk as the old file shows it
    (context and removed lines); for an added line, as the new file shows it.
    """
    blocks: List[ChangeBlock] = []
    old_view: List[str] = []
    new_view: List[str] = []
    block: Optional[ChangeBlock] = None
    for tag, text in hunk:
        if tag == " ":
            block = None
            old_view.append(text)
            new_view.append(text)
            continue
        if block is None:
            block = ChangeBlock(removed=[], added=[])
            blocks.append(block)
        if tag == "-":
            block.removed.append((text, list(old_view)))
            old_view.append(text)
        else:
            block.added.append((text, list(new_view)))
            new_view.append(text)
    return blocks
