"""Turn the manifest changes of a pull request diff into dependency updates.

Only the diff is read. Each changed line is parsed by the parser of the file's ecosystem; a
changed line that no parser can explain makes the pull request unevaluable, so that a pull
request is never proposed as obsolete because of a change the analysis did not understand.

The supported formats, identities, and failure reasons are documented in
references/manifest-formats.md - keep both in sync.
"""

from __future__ import annotations

import posixpath
import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from .diffparse import DiffFile, change_blocks


@dataclass(frozen=True)
class Entry:
    """One dependency reference found on a changed line."""

    ecosystem: str
    name: str
    value: str
    hint: Optional[str] = None  # human-readable version behind an opaque value


@dataclass(frozen=True)
class Update:
    ecosystem: str
    name: str
    path: str
    from_value: str
    to_value: str
    to_hint: Optional[str] = None
    from_hint: Optional[str] = None

    @property
    def identity(self) -> Tuple[str, str, str]:
        return (self.ecosystem, self.name, self.path)


class Unparsed(Exception):
    """A changed line could not be explained."""


# --------------------------------------------------------------------------------------------
# File classification

LOCKFILES = {
    "package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb",
    "bun.lock", "packages.lock.json", "poetry.lock", "pipfile.lock", "uv.lock", "pdm.lock",
    "gradle.lockfile", "buildscript-gradle.lockfile", "composer.lock", "gemfile.lock",
    "cargo.lock", "go.sum", "pubspec.lock", "mix.lock", "flake.lock",
}


def classify(path: str) -> Optional[str]:
    """Return the parser kind for a path, "lockfile", or None when unsupported."""
    lower = path.lower()
    base = posixpath.basename(lower)
    if base in LOCKFILES or base.endswith(".lockfile"):
        return "lockfile"
    if base == "package.json":
        return "npm"
    if base.endswith((".csproj", ".fsproj", ".vbproj", ".props", ".targets")) or base == "packages.config":
        return "nuget-xml"
    if base in ("dotnet-tools.json", "global.json"):
        return "nuget-json"
    if base == "pom.xml":
        return "maven"
    if base in ("build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"):
        return "gradle"
    if base == "gradle.properties":
        return "gradle-properties"
    if base.endswith(".versions.toml"):
        return "gradle-catalog"
    if re.search(r"(^|/)\.github/workflows/[^/]+\.ya?ml$", lower) or base in ("action.yml", "action.yaml"):
        return "github-actions"
    if base in ("dockerfile", "containerfile") or base.endswith(".dockerfile") or base.startswith("dockerfile."):
        return "dockerfile"
    if re.match(r"^(docker-)?compose([.-][^/]*)?\.ya?ml$", base):
        return "compose"
    if (re.match(r"^(requirements|constraints)[^/]*\.(txt|in)$", base)
            or re.search(r"(^|/)requirements/[^/]+\.(txt|in)$", lower)):
        return "pip-requirements"
    if base in ("pyproject.toml", "pipfile"):
        return "python-toml"
    if base == "setup.cfg":
        return "setup-cfg"
    return None


# --------------------------------------------------------------------------------------------
# Helpers

_COMMENT_PREFIXES = ("#", "//", "<!--", ";")

_RENOVATE_ANNOTATION = re.compile(
    r"renovate:\s*(?:datasource=(?P<ds>\S+))?.*?(?:depName|packageName)=(?P<dep>[^\s,]+)", re.IGNORECASE)


def _renovate_annotation(context: List[str]) -> Optional[Tuple[str, str]]:
    """The `# renovate: datasource=x depName=y` comment block directly above a line, if any."""
    for line in reversed(context):
        stripped = line.strip()
        if not stripped.startswith(_COMMENT_PREFIXES):
            return None  # the annotation must sit directly above, separated only by comments
        match = _RENOVATE_ANNOTATION.search(stripped)
        if match:
            return (match.group("ds") or "unknown", match.group("dep"))
    return None


_ANNOTATED_VALUE = re.compile(r"(?:[:=]|\s)\s*[\"']?(?P<value>v?\d[\w.+-]*)[\"']?\s*(?:#.*)?$")


def _parse_annotated(text: str, context: List[str]) -> Optional[Entry]:
    annotation = _renovate_annotation(context)
    if not annotation:
        return None
    match = _ANNOTATED_VALUE.search(text.strip())
    if not match:
        return None
    datasource, dep = annotation
    return Entry("renovate-annotated:" + datasource, dep, match.group("value"))


def _attr(text: str, name: str) -> Optional[str]:
    match = re.search(r"\b" + name + r"\s*=\s*\"([^\"]*)\"", text, re.IGNORECASE) or \
        re.search(r"\b" + name + r"\s*=\s*'([^']*)'", text, re.IGNORECASE)
    return match.group(1) if match else None


_XML_SIMPLE = re.compile(r"^\s*<(?P<tag>[A-Za-z_][\w.:-]*)>(?P<value>[^<]*)</(?P=tag)>\s*$")


# --------------------------------------------------------------------------------------------
# Ecosystem parsers: (text, context) -> List[Entry]; raise Unparsed when the line is not understood.

_NPM_LINE = re.compile(r'^\s*"(?P<name>[^"]+)"\s*:\s*"(?P<spec>[^"]*)"\s*,?\s*$')
_NPM_NON_DEPENDENCY_KEYS = {"name", "description", "main", "module", "types", "typings", "license",
                            "homepage", "author", "repository", "type", "private"}


def _parse_npm(text: str, context: List[str]) -> List[Entry]:
    match = _NPM_LINE.match(text)
    if not match:
        raise Unparsed("not a \"name\": \"version\" line")
    name, spec = match.group("name"), match.group("spec")
    if name == "packageManager":
        manager, _, version = spec.partition("@")
        return [Entry("npm", "packageManager:" + manager, version.split("+", 1)[0])]
    if name in _NPM_NON_DEPENDENCY_KEYS or name == "version":
        raise Unparsed("package.json key \"%s\" is not a dependency" % name)
    return [Entry("npm", name, spec)]


def _parse_nuget_xml(text: str, context: List[str]) -> List[Entry]:
    stripped = text.strip()
    element = re.match(r"^<(?P<el>PackageReference|PackageVersion|GlobalPackageReference|package|Sdk)\b", stripped)
    if element:
        el = element.group("el")
        name = _attr(stripped, "id") if el == "package" else (
            _attr(stripped, "Include") or _attr(stripped, "Update") or _attr(stripped, "Name"))
        version = _attr(stripped, "VersionOverride") or _attr(stripped, "Version") or _attr(stripped, "version")
        if not name or version is None:
            raise Unparsed("<%s> without name or version attribute" % el)
        return [Entry("nuget", name, version)]
    project_sdk = re.match(r"^<Project\b.*\bSdk\s*=\s*\"(?P<name>[^\"/]+)/(?P<ver>[^\"]+)\"", stripped)
    if project_sdk:
        return [Entry("nuget", project_sdk.group("name"), project_sdk.group("ver"))]
    simple = _XML_SIMPLE.match(text)
    if simple:
        tag, value = simple.group("tag"), simple.group("value")
        if tag in ("Version", "VersionOverride"):
            for line in reversed(context[-6:]):
                owner = re.search(r"<(PackageReference|PackageVersion|GlobalPackageReference)\b", line)
                if owner:
                    name = _attr(line, "Include") or _attr(line, "Update")
                    if name:
                        return [Entry("nuget", name, value)]
            raise Unparsed("<%s> without an enclosing package reference in the diff context" % tag)
        return [Entry("nuget", "msbuild-property:" + tag, value)]
    raise Unparsed("not a package reference, SDK, or property line")


_JSON_PAIR = re.compile(r'^\s*"(?P<key>[^"]+)"\s*:\s*"(?P<value>[^"]*)"\s*,?\s*$')
_JSON_OBJECT_OPEN = re.compile(r'^\s*"(?P<key>[^"]+)"\s*:\s*\{\s*$')


def _parse_nuget_json(text: str, context: List[str]) -> List[Entry]:
    match = _JSON_PAIR.match(text)
    if not match:
        raise Unparsed("not a \"key\": \"value\" line")
    key, value = match.group("key"), match.group("value")
    if key == "version":
        for line in reversed(context):
            owner = _JSON_OBJECT_OPEN.match(line)
            if owner:
                return [Entry("nuget", owner.group("key"), value)]
        raise Unparsed("\"version\" without its owning object in the diff context")
    if re.match(r"^\d", value):  # msbuild-sdks: "Name": "1.2.3"
        return [Entry("nuget", key, value)]
    raise Unparsed("JSON key \"%s\" is not a version" % key)


_MAVEN_STRUCTURAL = {"groupId", "artifactId", "scope", "type", "classifier", "optional", "packaging",
                     "modelVersion", "name", "description", "url", "id", "phase", "goal", "relativePath",
                     "module", "directory", "finalName", "source", "target", "release"}


def _parse_maven(text: str, context: List[str]) -> List[Entry]:
    simple = _XML_SIMPLE.match(text)
    if not simple:
        raise Unparsed("not a single-line XML element")
    tag, value = simple.group("tag"), simple.group("value")
    if tag == "version":
        group_id = artifact_id = None
        for line in reversed(context[-8:]):
            if re.search(r"<(dependency|plugin|parent|extension)>", line):
                break
            if re.search(r"</(dependency|plugin|parent|extension)>", line):
                break
            inner = _XML_SIMPLE.match(line)
            if inner and inner.group("tag") == "artifactId" and artifact_id is None:
                artifact_id = inner.group("value")
            if inner and inner.group("tag") == "groupId" and group_id is None:
                group_id = inner.group("value")
        if not artifact_id:
            raise Unparsed("<version> without <artifactId> in the diff context")
        return [Entry("maven", "%s:%s" % (group_id or "org.apache.maven.plugins", artifact_id), value)]
    if tag in _MAVEN_STRUCTURAL:
        raise Unparsed("<%s> is not a version" % tag)
    return [Entry("maven", "maven-property:" + tag, value)]


_GRADLE_COORDINATE = re.compile(r"[\"'](?P<group>[\w.-]+):(?P<artifact>[\w.-]+):(?P<version>[^\"':@\s]+)(?::[\w.-]+)?(?:@\w+)?[\"']")
_GRADLE_PLUGIN = re.compile(r"\bid\s*\(?\s*[\"'](?P<id>[\w.-]+)[\"']\s*\)?\s*version\s*\(?\s*[\"'](?P<version>[^\"']+)[\"']")
_GRADLE_KOTLIN_PLUGIN = re.compile(r"\bkotlin\s*\(\s*[\"'](?P<id>[\w.-]+)[\"']\s*\)\s*version\s*[\"'](?P<version>[^\"']+)[\"']")
_GRADLE_VARIABLE = re.compile(r"^\s*(?:val|var|def|const\s+val|ext\.)?\s*(?P<name>[A-Za-z_][\w.]*)\s*(?::\s*String\s*)?=\s*[\"'](?P<version>\d[^\"']*)[\"']\s*$")
_GRADLE_SET = re.compile(r"^\s*set\s*\(\s*[\"'](?P<name>[\w.-]+)[\"']\s*,\s*[\"'](?P<version>[^\"']+)[\"']\s*\)\s*$")


def _parse_gradle(text: str, context: List[str]) -> List[Entry]:
    entries = [Entry("gradle", "%s:%s" % (m.group("group"), m.group("artifact")), m.group("version"))
               for m in _GRADLE_COORDINATE.finditer(text)]
    entries += [Entry("gradle", "plugin:" + m.group("id"), m.group("version")) for m in _GRADLE_PLUGIN.finditer(text)]
    entries += [Entry("gradle", "plugin:org.jetbrains.kotlin." + m.group("id"), m.group("version"))
                for m in _GRADLE_KOTLIN_PLUGIN.finditer(text)]
    if entries:
        return entries
    for pattern in (_GRADLE_VARIABLE, _GRADLE_SET):
        match = pattern.match(text)
        if match:
            return [Entry("gradle", "gradle-variable:" + match.group("name"), match.group("version"))]
    raise Unparsed("no dependency coordinate, plugin version, or version variable")


def _parse_gradle_properties(text: str, context: List[str]) -> List[Entry]:
    match = re.match(r"^\s*(?P<key>[\w.-]+)\s*[=:]\s*(?P<value>\S+)\s*$", text)
    if not match or not re.match(r"^v?\d", match.group("value")):
        raise Unparsed("not a key=version line")
    return [Entry("gradle", "gradle-property:" + match.group("key"), match.group("value"))]


_TOML_PAIR = re.compile(r"^\s*(?P<key>[\w.-]+|\"[^\"]+\")\s*=\s*(?P<value>.+?)\s*(?:#.*)?$")


def _toml_inline(value: str) -> Dict[str, str]:
    return {m.group(1): m.group(2) for m in re.finditer(r"([\w.-]+)\s*=\s*\"([^\"]*)\"", value)}


def _parse_gradle_catalog(text: str, context: List[str]) -> List[Entry]:
    match = _TOML_PAIR.match(text)
    if not match:
        raise Unparsed("not a TOML key = value line")
    key, value = match.group("key").strip('"'), match.group("value").strip()
    if value.startswith('"'):
        literal = value.strip('"')
        coordinate = re.match(r"^(?P<module>[\w.-]+:[\w.-]+):(?P<version>.+)$", literal)
        if coordinate:
            return [Entry("gradle", coordinate.group("module"), coordinate.group("version"))]
        return [Entry("gradle", "catalog-version:" + key, literal)]
    if value.startswith("{"):
        fields = _toml_inline(value)
        version = fields.get("version")
        if version is None:
            raise Unparsed("catalog entry without a literal version (version.ref changes are not updates)")
        if "module" in fields:
            return [Entry("gradle", fields["module"], version)]
        if "group" in fields and "name" in fields:
            return [Entry("gradle", "%s:%s" % (fields["group"], fields["name"]), version)]
        if "id" in fields:
            return [Entry("gradle", "plugin:" + fields["id"], version)]
        raise Unparsed("catalog entry without module, group/name, or id")
    raise Unparsed("unsupported TOML value")


_USES_DOCKER = re.compile(r"^\s*(?:-\s*)?uses:\s*[\"']?docker://(?P<image>[^\s\"'#]+)[\"']?\s*(?:#.*)?$")
_USES = re.compile(r"^\s*(?:-\s*)?uses:\s*[\"']?(?P<ref>[^@\s\"']+)@(?P<ver>[^\s\"'#]+)[\"']?\s*(?:#\s*(?P<comment>\S+).*)?$")
_YAML_IMAGE = re.compile(r"^\s*(?:-\s*)?image:\s*[\"']?(?P<image>[^\s\"'#]+)[\"']?\s*(?:#.*)?$")


def _split_image(reference: str) -> Tuple[str, str, Optional[str]]:
    """Split `registry/name:tag@sha256:...` into (name, exact value, orderable tag)."""
    digest = None
    if "@" in reference:
        reference, digest = reference.split("@", 1)
    name, tag = reference, None
    last = reference.rsplit("/", 1)[-1]
    if ":" in last:
        name, tag = reference.rsplit(":", 1)
    if tag is None and digest is None:
        raise Unparsed("image without tag or digest")
    exact = (tag or "") + ("@" + digest if digest else "")
    return name, exact, tag


def _image_entry(reference: str) -> Entry:
    name, exact, tag = _split_image(reference)
    return Entry("docker", name, exact, hint=tag if tag and exact != tag else None)


def _parse_github_actions(text: str, context: List[str]) -> List[Entry]:
    docker = _USES_DOCKER.match(text)
    if docker:
        return [_image_entry(docker.group("image"))]
    match = _USES.match(text)
    if match:
        ref, ver, comment = match.group("ref"), match.group("ver"), match.group("comment")
        sha = re.match(r"^[0-9a-f]{40}$", ver)
        return [Entry("github-actions", ref, ver, hint=comment if sha and comment else None)]
    image = _YAML_IMAGE.match(text)
    if image:
        return [_image_entry(image.group("image"))]
    raise Unparsed("not a uses: or image: line")


_FROM = re.compile(r"^\s*FROM\s+(?:--platform=\S+\s+)?(?P<image>\S+)(?:\s+AS\s+\S+)?\s*$", re.IGNORECASE)


def _parse_dockerfile(text: str, context: List[str]) -> List[Entry]:
    match = _FROM.match(text)
    if not match:
        raise Unparsed("not a FROM line")
    image = match.group("image")
    if "$" in image:
        raise Unparsed("FROM uses a build argument; its value is set elsewhere")
    return [_image_entry(image)]


def _parse_compose(text: str, context: List[str]) -> List[Entry]:
    match = _YAML_IMAGE.match(text)
    if not match:
        raise Unparsed("not an image: line")
    if "$" in match.group("image"):
        raise Unparsed("image uses a variable; its value is set elsewhere")
    return [_image_entry(match.group("image"))]


_PEP508 = re.compile(r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:\[[^\]]*\])?\s*(?P<spec>(?:[<>=!~]=?|===)[^;#]*?)?\s*(?:;.*)?$")


def _pep503(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _pep508_entry(requirement: str, allow_unversioned: bool = False) -> Entry:
    match = _PEP508.match(requirement.strip())
    if not match or not (match.group("spec") or allow_unversioned):
        raise Unparsed("requirement without a version specifier")
    # An unversioned entry next to the updated one on the same line ("wheel" in
    # requires = ["setuptools>=72", "wheel"]) pairs with itself and drops out as unchanged.
    return Entry("pypi", _pep503(match.group("name")), (match.group("spec") or "").strip())


def _parse_pip_requirements(text: str, context: List[str]) -> List[Entry]:
    stripped = text.split(" #", 1)[0].strip().rstrip("\\").strip()
    if stripped.startswith("-"):
        raise Unparsed("pip option line (-r, -e, --index-url, ...)")
    return [_pep508_entry(stripped)]


def _parse_python_toml(text: str, context: List[str]) -> List[Entry]:
    stripped = text.strip()
    # PEP 621 / build-system: quoted PEP 508 strings, one per line or several in an array.
    quoted = re.findall(r"\"([^\"]+)\"|'([^']+)'", stripped)
    pair = _TOML_PAIR.match(text)
    if pair and not stripped.startswith(("\"", "'")) and not pair.group("value").startswith("["):
        key, value = pair.group("key").strip('"'), pair.group("value").strip()
        if key in ("version", "requires-python", "name", "description"):
            raise Unparsed("TOML key \"%s\" is not a dependency" % key)
        if value.startswith("{"):
            fields = _toml_inline(value)
            if "version" not in fields:
                raise Unparsed("inline dependency table without a version")
            return [Entry("pypi", _pep503(key), fields["version"])]
        return [Entry("pypi", _pep503(key), value.strip("\"'"))]
    if quoted:
        return [_pep508_entry(a or b, allow_unversioned=len(quoted) > 1) for a, b in quoted]
    raise Unparsed("not a dependency line")


def _parse_setup_cfg(text: str, context: List[str]) -> List[Entry]:
    stripped = text.strip()
    if "=" in stripped and not re.match(r"^[A-Za-z0-9._-]+\s*(\[[^\]]*\])?\s*(==|>=|<=|~=|!=|===)", stripped):
        stripped = stripped.split("=", 1)[1].strip()  # "install_requires = requests>=2"
    return [_pep508_entry(stripped)]


PARSERS: Dict[str, Callable[[str, List[str]], List[Entry]]] = {
    "npm": _parse_npm,
    "nuget-xml": _parse_nuget_xml,
    "nuget-json": _parse_nuget_json,
    "maven": _parse_maven,
    "gradle": _parse_gradle,
    "gradle-properties": _parse_gradle_properties,
    "gradle-catalog": _parse_gradle_catalog,
    "github-actions": _parse_github_actions,
    "dockerfile": _parse_dockerfile,
    "compose": _parse_compose,
    "pip-requirements": _parse_pip_requirements,
    "python-toml": _parse_python_toml,
    "setup-cfg": _parse_setup_cfg,
}


# --------------------------------------------------------------------------------------------
# Diff -> updates

@dataclass
class FileResult:
    path: str
    kind: Optional[str]
    updates: List[Update]
    problems: List[str]


def _is_ignorable(text: str, kind: Optional[str]) -> bool:
    stripped = text.strip()
    if stripped == "":
        return True
    if kind == "pip-requirements" and stripped.startswith("--hash="):
        return True  # hash continuation lines of pip-compile output belong to the line above
    return stripped.startswith(_COMMENT_PREFIXES)


def _entries(text: str, context: List[str], kind: Optional[str]) -> List[Entry]:
    parser = PARSERS.get(kind) if kind else None
    if parser is not None:
        try:
            return parser(text, context)
        except Unparsed as error:
            annotated = _parse_annotated(text, context)
            if annotated:
                return [annotated]
            raise error
    annotated = _parse_annotated(text, context)
    if annotated:
        return [annotated]
    raise Unparsed("unsupported file type")


def analyse_file(diff_file: DiffFile) -> FileResult:
    path = diff_file.path
    kind = classify(path)
    result = FileResult(path=path, kind=kind, updates=[], problems=[])
    if kind == "lockfile":
        return result
    if diff_file.binary:
        result.problems.append("%s: binary file" % path)
        return result
    if diff_file.status in ("added", "deleted", "renamed"):
        result.problems.append("%s: file %s (only in-place version changes are evaluated)" % (path, diff_file.status))
        return result

    seen = set()
    for hunk in diff_file.hunks:
        for block in change_blocks(hunk):
            removed: Dict[Tuple[str, str], List[Entry]] = {}
            added: Dict[Tuple[str, str], List[Entry]] = {}
            for side, store in ((block.removed, removed), (block.added, added)):
                for text, context in side:
                    if _is_ignorable(text, kind):
                        continue
                    try:
                        for entry in _entries(text, context, kind):
                            store.setdefault((entry.ecosystem, entry.name), []).append(entry)
                    except Unparsed as error:
                        result.problems.append("%s: cannot interpret %r (%s)" % (path, text.strip()[:120], error))
            for key in sorted(set(removed) | set(added)):
                olds, news = removed.get(key, []), added.get(key, [])
                if len(olds) != len(news):
                    result.problems.append("%s: %s is added or removed, not updated" % (path, key[1]))
                    continue
                for old, new in zip(olds, news):
                    if old.value == new.value and old.hint == new.hint:
                        continue  # reformatting only
                    update = Update(key[0], key[1], path, old.value, new.value, new.hint, old.hint)
                    if update not in seen:
                        seen.add(update)
                        result.updates.append(update)
    return result
