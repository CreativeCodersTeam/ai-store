#!/usr/bin/env bash
# Validates every SKILL.md against the Agent Skills specification
# (https://agentskills.io/specification) and every .claude-plugin/plugin.json
# against the skills it claims to ship.
#
# Checks per SKILL.md:
#   - YAML frontmatter present and delimited by --- at the top of the file
#   - name: present, 1-64 chars, [a-z0-9-] only, no leading/trailing/double hyphen
#   - name: equal to the parent directory name
#   - description: present, non-empty, <= 1024 characters
#     (GitHub Copilot silently drops a skill whose description exceeds this;
#      Claude Code loads it anyway, so the defect is invisible without this check)
#
# Checks per plugin manifest:
#   - every path in "skills" resolves to a directory containing SKILL.md
#   - every skill directory next to the manifest is listed in "skills"
#     (a new skill added to a category must be added to its plugin too)
#
# Checks the marketplace manifest (.claude-plugin/marketplace.json):
#   - required fields: name, owner.name, plugins[]
#   - plugin names are unique and kebab-case
#   - every relative "source" resolves to a directory holding a plugin manifest
#   - the marketplace entry name matches the name in that plugin manifest
#   - every plugin manifest in the repository is listed in the marketplace
#
# Usage: bash scripts/validate-skills.sh [--warn-at N]
#   --warn-at N   Print a warning for descriptions longer than N chars
#                 without failing. Default 900.
#
# Exit codes: 0 all checks passed / 1 validation failures / 2 usage or missing dependency

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WARN_AT=900

while [[ $# -gt 0 ]]; do
  case "$1" in
    --warn-at) [[ $# -ge 2 ]] || { echo "ERROR: --warn-at needs a value" >&2; exit 2; }
               WARN_AT="$2"; shift 2 ;;
    -h|--help) sed -n '2,25p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)         echo "ERROR: unknown argument: $1" >&2; exit 2 ;;
  esac
done

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is required" >&2
  exit 2
fi

REPO_ROOT="$REPO_ROOT" WARN_AT="$WARN_AT" python3 - <<'PY'
import json, os, re, sys

ROOT = os.environ["REPO_ROOT"]
WARN_AT = int(os.environ["WARN_AT"])
MAX_DESC = 1024
MAX_NAME = 64
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

RED, GREEN, YELLOW, OFF = "\033[31m", "\033[32m", "\033[33m", "\033[0m"
if not sys.stdout.isatty():
    RED = GREEN = YELLOW = OFF = ""

errors, warnings, checked = [], [], 0


def rel(p):
    return os.path.relpath(p, ROOT)


def frontmatter(text):
    """Return the raw frontmatter block, or None if absent/unterminated."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 3)
    return None if end == -1 else text[4:end + 1]


def scalar(fm, key):
    """Read a top-level scalar, including folded (>) and literal (|) blocks."""
    lines = fm.split("\n")
    for i, line in enumerate(lines):
        if not line.startswith(key + ":"):
            continue
        head = line[len(key) + 1:].strip()
        if head not in (">", "|", ">-", "|-", ">+", "|+"):
            return head.strip("'\"")
        body = []
        for cont in lines[i + 1:]:
            if cont.strip() and not cont.startswith((" ", "\t")):
                break
            body.append(cont.strip())
        joined = " ".join(x for x in body if x)
        return joined if head.startswith(">") else "\n".join(x for x in body if x)
    return None


# ---------- SKILL.md ----------
skill_dirs = []
for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, "skills")):
    if "SKILL.md" not in filenames:
        continue
    skill_dirs.append(dirpath)
    checked += 1
    path = os.path.join(dirpath, "SKILL.md")
    where = rel(path)
    text = open(path, encoding="utf-8").read()

    fm = frontmatter(text)
    if fm is None:
        errors.append(f"{where}: no YAML frontmatter delimited by --- at the top of the file")
        continue

    name = scalar(fm, "name")
    expected = os.path.basename(dirpath)
    if not name:
        errors.append(f"{where}: frontmatter has no 'name'")
    else:
        if name != expected:
            errors.append(f"{where}: name '{name}' does not match directory name '{expected}'")
        if len(name) > MAX_NAME:
            errors.append(f"{where}: name is {len(name)} chars, max {MAX_NAME}")
        if not NAME_RE.match(name):
            errors.append(
                f"{where}: name '{name}' is not lowercase [a-z0-9] with single hyphens")

    desc = scalar(fm, "description")
    if not desc:
        errors.append(f"{where}: frontmatter has no non-empty 'description'")
    elif len(desc) > MAX_DESC:
        errors.append(
            f"{where}: description is {len(desc)} chars, max {MAX_DESC} "
            f"(GitHub Copilot drops this skill silently)")
    elif len(desc) > WARN_AT:
        warnings.append(f"{where}: description is {len(desc)} chars, approaching the {MAX_DESC} limit")

# ---------- plugin.json ----------
for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, "skills")):
    manifest = os.path.join(dirpath, ".claude-plugin", "plugin.json")
    if not os.path.isfile(manifest):
        continue
    where = rel(manifest)
    try:
        data = json.load(open(manifest, encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{where}: invalid JSON: {exc}")
        continue

    declared = data.get("skills")
    if declared is None:
        continue
    if isinstance(declared, str):
        declared = [declared]

    resolved = set()
    for entry in declared:
        target = os.path.normpath(os.path.join(dirpath, entry))
        resolved.add(target)
        if not os.path.isfile(os.path.join(target, "SKILL.md")):
            errors.append(f"{where}: skills entry '{entry}' has no SKILL.md")

    on_disk = {d for d in skill_dirs if os.path.dirname(d) == dirpath}
    for missing in sorted(on_disk - resolved):
        errors.append(
            f"{where}: skill '{os.path.basename(missing)}' exists on disk but is not "
            f"listed in 'skills' — it will not ship with the plugin")

# ---------- marketplace.json ----------
MARKET = os.path.join(ROOT, ".claude-plugin", "marketplace.json")
manifests_on_disk = set()
for dirpath, _, _ in os.walk(os.path.join(ROOT, "skills")):
    if os.path.isfile(os.path.join(dirpath, ".claude-plugin", "plugin.json")):
        manifests_on_disk.add(dirpath)

if not os.path.isfile(MARKET):
    if manifests_on_disk:
        errors.append(
            ".claude-plugin/marketplace.json is missing, but plugin manifests exist on disk")
else:
    where = rel(MARKET)
    try:
        market = json.load(open(MARKET, encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{where}: invalid JSON: {exc}")
        market = None

    if market is not None:
        if not market.get("name"):
            errors.append(f"{where}: missing required field 'name'")
        elif not NAME_RE.match(market["name"]):
            errors.append(f"{where}: name '{market['name']}' is not kebab-case")
        if not isinstance(market.get("owner"), dict) or not market["owner"].get("name"):
            errors.append(f"{where}: missing required field 'owner.name'")

        entries = market.get("plugins")
        if not isinstance(entries, list) or not entries:
            errors.append(f"{where}: 'plugins' must be a non-empty array")
            entries = []

        seen, listed = set(), set()
        for i, entry in enumerate(entries):
            at = f"{where}: plugins[{i}]"
            pname = entry.get("name")
            if not pname:
                errors.append(f"{at}: missing 'name'")
            else:
                if pname in seen:
                    errors.append(f"{at}: duplicate plugin name '{pname}'")
                seen.add(pname)
                if not NAME_RE.match(pname):
                    errors.append(f"{at}: name '{pname}' is not kebab-case")

            src = entry.get("source")
            if src is None:
                errors.append(f"{at}: missing 'source'")
                continue
            if not isinstance(src, str):
                continue  # github/url/npm sources are resolved at install time, not here
            if ".." in src.split("/"):
                errors.append(f"{at}: source '{src}' escapes the marketplace root")
                continue
            target = os.path.normpath(os.path.join(ROOT, src))
            listed.add(target)
            plugin_manifest = os.path.join(target, ".claude-plugin", "plugin.json")
            if not os.path.isfile(plugin_manifest):
                errors.append(f"{at}: source '{src}' has no .claude-plugin/plugin.json")
                continue
            try:
                declared_name = json.load(open(plugin_manifest, encoding="utf-8")).get("name")
            except json.JSONDecodeError:
                continue  # already reported above
            if pname and declared_name != pname:
                errors.append(
                    f"{at}: marketplace calls this plugin '{pname}' but "
                    f"{rel(plugin_manifest)} declares name '{declared_name}'")

        for orphan in sorted(manifests_on_disk - listed):
            errors.append(
                f"{where}: {rel(orphan)} has a .claude-plugin/plugin.json but is not "
                f"listed in 'plugins' — it is not installable")

# ---------- report ----------
for w in warnings:
    print(f"  {YELLOW}WARN{OFF} {w}")
for e in errors:
    print(f"  {RED}FAIL{OFF} {e}")

print()
if errors:
    print(f"{RED}{len(errors)} error(s){OFF}, {len(warnings)} warning(s), {checked} SKILL.md checked")
    sys.exit(1)
print(f"{GREEN}OK{OFF} — {checked} SKILL.md checked, {len(warnings)} warning(s)")
PY
