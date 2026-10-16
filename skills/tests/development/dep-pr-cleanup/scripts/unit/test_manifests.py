import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers import file_diff, hunk, lockfile, npm  # noqa: E402

from deplib.diffparse import parse_diff  # noqa: E402
from deplib.manifests import analyse_file, classify  # noqa: E402


def analyse(diff):
    updates, problems, kinds = [], [], []
    for diff_file in parse_diff(diff):
        result = analyse_file(diff_file)
        updates += result.updates
        problems += result.problems
        kinds.append(result.kind)
    return updates, problems, kinds


def triples(updates):
    return sorted((u.name, u.from_value, u.to_value) for u in updates)


class ClassifyTest(unittest.TestCase):
    def test_paths(self):
        cases = {
            "web/package.json": "npm", "package-lock.json": "lockfile", "yarn.lock": "lockfile",
            "src/App/App.csproj": "nuget-xml", "Directory.Packages.props": "nuget-xml",
            "packages.config": "nuget-xml", ".config/dotnet-tools.json": "nuget-json",
            "packages.lock.json": "lockfile", "pom.xml": "maven", "build.gradle.kts": "gradle",
            "gradle/libs.versions.toml": "gradle-catalog", "gradle.properties": "gradle-properties",
            ".github/workflows/ci.yml": "github-actions", "actions/setup/action.yaml": "github-actions",
            "Dockerfile": "dockerfile", "docker/api.Dockerfile": "dockerfile", "Dockerfile.dev": "dockerfile",
            "docker-compose.yml": "compose", "compose.prod.yaml": "compose",
            "requirements.txt": "pip-requirements", "requirements-dev.txt": "pip-requirements",
            "requirements/base.in": "pip-requirements", "pyproject.toml": "python-toml",
            "Pipfile": "python-toml", "Pipfile.lock": "lockfile", "poetry.lock": "lockfile",
            "setup.cfg": "setup-cfg", "Cargo.toml": None, ".github/workflows/README.md": None,
        }
        for path, expected in cases.items():
            self.assertEqual(classify(path), expected, path)


class NpmTest(unittest.TestCase):
    def test_dependency_update(self):
        updates, problems, _ = analyse(npm("web/package.json", ("lodash", "^4.17.20", "^4.17.21"),
                                           ("@types/node", "20.1.0", "20.2.0")))
        self.assertEqual(problems, [])
        self.assertEqual(triples(updates), [("@types/node", "20.1.0", "20.2.0"), ("lodash", "^4.17.20", "^4.17.21")])
        self.assertTrue(all(u.path == "web/package.json" and u.ecosystem == "npm" for u in updates))

    def test_package_manager_field(self):
        diff = file_diff("package.json", hunk([], ['  "packageManager": "pnpm@9.1.0+sha512.abc",'],
                                               ['  "packageManager": "pnpm@9.4.0+sha512.def",']))
        updates, problems, _ = analyse(diff)
        self.assertEqual(problems, [])
        self.assertEqual(triples(updates), [("packageManager:pnpm", "9.1.0", "9.4.0")])

    def test_lockfile_is_ignored(self):
        updates, problems, kinds = analyse(lockfile())
        self.assertEqual((updates, problems, kinds), ([], [], ["lockfile"]))

    def test_unknown_line_is_a_problem(self):
        diff = file_diff("package.json", hunk([], ['  "version": "1.0.0",'], ['  "version": "1.0.1",']))
        updates, problems, _ = analyse(diff)
        self.assertEqual(updates, [])
        self.assertEqual(len(problems), 2)

    def test_added_dependency_is_not_an_update(self):
        diff = file_diff("package.json", hunk(['  "dependencies": {'], [], ['    "left-pad": "1.3.0",']))
        updates, problems, _ = analyse(diff)
        self.assertEqual(updates, [])
        self.assertIn("added or removed", problems[0])

    def test_reformatting_only_produces_nothing(self):
        diff = file_diff("package.json", hunk([], ['    "a": "1.0.0",'], ['    "a":  "1.0.0" ,']))
        updates, problems, _ = analyse(diff)
        self.assertEqual((updates, problems), ([], []))


class NuGetTest(unittest.TestCase):
    def test_package_reference_attributes(self):
        diff = file_diff("src/Api/Api.csproj", hunk(
            ["  <ItemGroup>"],
            ['    <PackageReference Include="Serilog" Version="3.1.0" />',
             '    <PackageReference Version="8.0.0" Include="Polly" />'],
            ['    <PackageReference Include="Serilog" Version="4.0.0" />',
             '    <PackageReference Version="8.1.0" Include="Polly" />']))
        updates, problems, _ = analyse(diff)
        self.assertEqual(problems, [])
        self.assertEqual(triples(updates), [("Polly", "8.0.0", "8.1.0"), ("Serilog", "3.1.0", "4.0.0")])

    def test_central_package_management_and_packages_config(self):
        diff = file_diff("Directory.Packages.props", hunk(
            [], ['    <PackageVersion Include="xunit" Version="2.6.0" />'],
            ['    <PackageVersion Include="xunit" Version="2.9.0" />'])) + \
            file_diff("legacy/packages.config", hunk(
                [], ['  <package id="Newtonsoft.Json" version="12.0.3" targetFramework="net48" />'],
                ['  <package id="Newtonsoft.Json" version="13.0.3" targetFramework="net48" />']))
        updates, problems, _ = analyse(diff)
        self.assertEqual(problems, [])
        self.assertEqual(triples(updates), [("Newtonsoft.Json", "12.0.3", "13.0.3"), ("xunit", "2.6.0", "2.9.0")])

    def test_multiline_reference_uses_context(self):
        diff = file_diff("App.csproj", hunk(['    <PackageReference Include="Dapper">'],
                                            ["      <Version>2.0.0</Version>"], ["      <Version>2.1.0</Version>"],
                                            ["    </PackageReference>"]))
        updates, problems, _ = analyse(diff)
        self.assertEqual(problems, [])
        self.assertEqual(triples(updates), [("Dapper", "2.0.0", "2.1.0")])

    def test_msbuild_property_is_its_own_identity(self):
        diff = file_diff("Directory.Build.props", hunk(["  <PropertyGroup>"], ["    <AspireVersion>9.0.0</AspireVersion>"],
                                                       ["    <AspireVersion>9.1.0</AspireVersion>"]))
        updates, _, _ = analyse(diff)
        self.assertEqual(triples(updates), [("msbuild-property:AspireVersion", "9.0.0", "9.1.0")])

    def test_dotnet_tools_json(self):
        diff = file_diff(".config/dotnet-tools.json", hunk(['    "dotnet-ef": {'], ['      "version": "8.0.0",'],
                                                           ['      "version": "8.0.8",']))
        updates, problems, _ = analyse(diff)
        self.assertEqual(problems, [])
        self.assertEqual(triples(updates), [("dotnet-ef", "8.0.0", "8.0.8")])


class MavenGradleTest(unittest.TestCase):
    def test_pom_dependency_version_uses_context(self):
        diff = file_diff("pom.xml", hunk(["    <dependency>", "      <groupId>com.google.guava</groupId>",
                                          "      <artifactId>guava</artifactId>"],
                                         ["      <version>32.1.3-jre</version>"], ["      <version>33.0.0-jre</version>"],
                                         ["    </dependency>"]))
        updates, problems, _ = analyse(diff)
        self.assertEqual(problems, [])
        self.assertEqual(triples(updates), [("com.google.guava:guava", "32.1.3-jre", "33.0.0-jre")])

    def test_pom_parent_and_property(self):
        diff = file_diff("pom.xml", hunk(["  <parent>", "    <groupId>org.springframework.boot</groupId>",
                                          "    <artifactId>spring-boot-starter-parent</artifactId>"],
                                         ["    <version>3.3.1</version>"], ["    <version>3.3.4</version>"])
                         + hunk(["  <properties>"], ["    <testcontainers.version>1.19.0</testcontainers.version>"],
                                ["    <testcontainers.version>1.20.1</testcontainers.version>"]))
        updates, problems, _ = analyse(diff)
        self.assertEqual(problems, [])
        self.assertEqual(triples(updates), [
            ("maven-property:testcontainers.version", "1.19.0", "1.20.1"),
            ("org.springframework.boot:spring-boot-starter-parent", "3.3.1", "3.3.4")])

    def test_pom_version_without_artifact_in_context(self):
        diff = file_diff("pom.xml", hunk([], ["      <version>1.0</version>"], ["      <version>1.1</version>"]))
        _, problems, _ = analyse(diff)
        self.assertTrue(problems and "artifactId" in problems[0])

    def test_gradle_forms(self):
        diff = file_diff("build.gradle.kts", hunk(
            ["plugins {"],
            ['    id("org.springframework.boot") version "3.3.1"', '    kotlin("jvm") version "1.9.24"'],
            ['    id("org.springframework.boot") version "3.3.4"', '    kotlin("jvm") version "2.0.0"'])
            + hunk(["dependencies {"], ['    implementation("org.flywaydb:flyway-core:10.10.0")'],
                   ['    implementation("org.flywaydb:flyway-core:10.17.0")'])
            + hunk([], ['val ktorVersion = "2.3.10"'], ['val ktorVersion = "2.3.12"']))
        updates, problems, _ = analyse(diff)
        self.assertEqual(problems, [])
        self.assertEqual(triples(updates), [
            ("gradle-variable:ktorVersion", "2.3.10", "2.3.12"),
            ("org.flywaydb:flyway-core", "10.10.0", "10.17.0"),
            ("plugin:org.jetbrains.kotlin.jvm", "1.9.24", "2.0.0"),
            ("plugin:org.springframework.boot", "3.3.1", "3.3.4")])

    def test_groovy_and_properties(self):
        diff = file_diff("build.gradle", hunk([], ["    testImplementation 'org.junit.jupiter:junit-jupiter:5.10.0'"],
                                              ["    testImplementation 'org.junit.jupiter:junit-jupiter:5.11.0'"])) + \
            file_diff("gradle.properties", hunk([], ["kotlinVersion=1.9.24"], ["kotlinVersion=2.0.0"]))
        updates, problems, _ = analyse(diff)
        self.assertEqual(problems, [])
        self.assertEqual(triples(updates), [("gradle-property:kotlinVersion", "1.9.24", "2.0.0"),
                                            ("org.junit.jupiter:junit-jupiter", "5.10.0", "5.11.0")])

    def test_version_catalog(self):
        diff = file_diff("gradle/libs.versions.toml", hunk(
            ["[versions]"], ['spring-boot = "3.3.1"'], ['spring-boot = "3.3.4"'])
            + hunk(["[libraries]"], ['jackson = { module = "com.fasterxml.jackson.core:jackson-databind", version = "2.17.0" }',
                                     'okhttp = "com.squareup.okhttp3:okhttp:4.11.0"'],
                   ['jackson = { module = "com.fasterxml.jackson.core:jackson-databind", version = "2.17.2" }',
                    'okhttp = "com.squareup.okhttp3:okhttp:4.12.0"'])
            + hunk(["[plugins]"], ['detekt = { id = "io.gitlab.arturbosch.detekt", version = "1.23.5" }'],
                   ['detekt = { id = "io.gitlab.arturbosch.detekt", version = "1.23.6" }']))
        updates, problems, _ = analyse(diff)
        self.assertEqual(problems, [])
        self.assertEqual(triples(updates), [
            ("catalog-version:spring-boot", "3.3.1", "3.3.4"),
            ("com.fasterxml.jackson.core:jackson-databind", "2.17.0", "2.17.2"),
            ("com.squareup.okhttp3:okhttp", "4.11.0", "4.12.0"),
            ("plugin:io.gitlab.arturbosch.detekt", "1.23.5", "1.23.6")])


class ActionsDockerTest(unittest.TestCase):
    def test_uses_tag_and_sha_pin(self):
        old_sha, new_sha = "a" * 40, "b" * 40
        diff = file_diff(".github/workflows/ci.yml", hunk(
            ["    steps:"], ["      - uses: actions/checkout@v4",
                             "      - uses: actions/setup-node@%s # v4.0.2" % old_sha],
            ["      - uses: actions/checkout@v5", "      - uses: actions/setup-node@%s # v4.1.0" % new_sha]))
        updates, problems, _ = analyse(diff)
        self.assertEqual(problems, [])
        self.assertEqual(triples(updates), [("actions/checkout", "v4", "v5"), ("actions/setup-node", old_sha, new_sha)])
        node = [u for u in updates if u.name == "actions/setup-node"][0]
        self.assertEqual((node.from_hint, node.to_hint), ("v4.0.2", "v4.1.0"))

    def test_docker_uses_and_container_image(self):
        diff = file_diff(".github/workflows/ci.yml", hunk(
            [], ["      - uses: docker://alpine:3.19", "    container: ", "      image: node:20-alpine"],
            ["      - uses: docker://alpine:3.20", "    container: ", "      image: node:22-alpine"]))
        updates, problems, _ = analyse(diff)
        self.assertEqual(triples(updates), [("alpine", "3.19", "3.20"), ("node", "20-alpine", "22-alpine")])
        self.assertTrue(problems)  # the unchanged-looking "container:" lines are not dependency lines

    def test_dockerfile_from_with_digest_and_stage(self):
        diff = file_diff("Dockerfile", hunk([], ["FROM --platform=$BUILDPLATFORM node:20.11-alpine@sha256:aaa AS build"],
                                            ["FROM --platform=$BUILDPLATFORM node:20.12-alpine@sha256:bbb AS build"]))
        updates, problems, _ = analyse(diff)
        self.assertEqual(problems, [])
        self.assertEqual(triples(updates), [("node", "20.11-alpine@sha256:aaa", "20.12-alpine@sha256:bbb")])
        self.assertEqual(updates[0].to_hint, "20.12-alpine")

    def test_dockerfile_build_arg_is_unevaluable(self):
        diff = file_diff("Dockerfile", hunk([], ["FROM node:${NODE_VERSION}"], ["FROM node:${NODE}"]))
        _, problems, _ = analyse(diff)
        self.assertTrue(problems)

    def test_compose_image(self):
        diff = file_diff("docker-compose.yml", hunk(["  db:"], ['    image: "postgres:16.3"'], ['    image: "postgres:16.4"']))
        updates, problems, _ = analyse(diff)
        self.assertEqual(problems, [])
        self.assertEqual(triples(updates), [("postgres", "16.3", "16.4")])

    def test_renovate_annotation_in_any_file(self):
        diff = file_diff(".github/workflows/pr.yaml", hunk(
            ["        with:", "          # renovate: datasource=github-releases depName=golangci/golangci-lint"],
            ["          version: v2.14.0"], ["          version: v2.15.0"])) + \
            file_diff("Makefile", hunk(["# renovate: datasource=github-releases depName=golangci/golangci-lint"],
                                       ["GOLANGCI_LINT_VERSION ?= v2.14.0"], ["GOLANGCI_LINT_VERSION ?= v2.15.0"]))
        updates, problems, _ = analyse(diff)
        self.assertEqual(problems, [])
        self.assertEqual([(u.ecosystem, u.name, u.path) for u in updates], [
            ("renovate-annotated:github-releases", "golangci/golangci-lint", ".github/workflows/pr.yaml"),
            ("renovate-annotated:github-releases", "golangci/golangci-lint", "Makefile")])

    def test_annotation_must_be_directly_above(self):
        diff = file_diff("Makefile", hunk(["# renovate: datasource=docker depName=node", "OTHER = 1"],
                                          ["NODE_VERSION = 20"], ["NODE_VERSION = 22"]))
        updates, problems, _ = analyse(diff)
        self.assertEqual(updates, [])
        self.assertTrue(problems)


class PythonTest(unittest.TestCase):
    def test_requirements_with_hashes_and_markers(self):
        diff = file_diff("requirements.txt", hunk(
            [], ["requests==2.31.0 \\", "    --hash=sha256:aaa", "Django>=4.2,<5 ; python_version >= '3.10'"],
            ["requests==2.32.3 \\", "    --hash=sha256:bbb", "Django>=4.2.16,<5 ; python_version >= '3.10'"]))
        updates, problems, _ = analyse(diff)
        self.assertEqual(problems, [])
        self.assertEqual(triples(updates), [("django", ">=4.2,<5", ">=4.2.16,<5"), ("requests", "==2.31.0", "==2.32.3")])

    def test_pyproject_pep621_and_poetry(self):
        diff = file_diff("pyproject.toml", hunk(
            ["dependencies = ["], ['    "httpx>=0.26.0",', '    "Pydantic[email]==2.6.0",'],
            ['    "httpx>=0.27.0",', '    "Pydantic[email]==2.8.2",'])
            + hunk(["[tool.poetry.dependencies]"], ['fastapi = "^0.110.0"', 'uvicorn = { version = "^0.29.0", extras = ["standard"] }'],
                   ['fastapi = "^0.112.0"', 'uvicorn = { version = "^0.30.1", extras = ["standard"] }'])
            + hunk(["[build-system]"], ['requires = ["setuptools>=68", "wheel"]'], ['requires = ["setuptools>=72", "wheel"]']))
        updates, problems, _ = analyse(diff)
        self.assertEqual(problems, [], problems)
        self.assertEqual(triples(updates), [
            ("fastapi", "^0.110.0", "^0.112.0"), ("httpx", ">=0.26.0", ">=0.27.0"),
            ("pydantic", "==2.6.0", "==2.8.2"), ("setuptools", ">=68", ">=72"), ("uvicorn", "^0.29.0", "^0.30.1")])

    def test_pipfile_and_setup_cfg(self):
        diff = file_diff("Pipfile", hunk(["[packages]"], ['flask = "==3.0.0"'], ['flask = "==3.0.3"'])) + \
            file_diff("setup.cfg", hunk(["install_requires ="], ["    click>=8.1.0"], ["    click>=8.1.7"]))
        updates, problems, _ = analyse(diff)
        self.assertEqual(problems, [])
        self.assertEqual(triples(updates), [("click", ">=8.1.0", ">=8.1.7"), ("flask", "==3.0.0", "==3.0.3")])


class FileStatusTest(unittest.TestCase):
    def test_unsupported_and_new_files(self):
        diff = file_diff("Cargo.toml", hunk([], ['serde = "1.0.1"'], ['serde = "1.0.2"']))
        diff += "diff --git a/new.txt b/new.txt\nnew file mode 100644\n--- /dev/null\n+++ b/new.txt\n@@ -0,0 +1 @@\n+x\n"
        updates, problems, _ = analyse(diff)
        self.assertEqual(updates, [])
        self.assertTrue(any("unsupported file type" in p for p in problems))
        self.assertTrue(any("file added" in p for p in problems))

    def test_crlf_diff(self):
        diff = npm("package.json", ("a", "1.0.0", "1.1.0")).replace("\n", "\r\n")
        updates, problems, _ = analyse(diff)
        self.assertEqual((triples(updates), problems), ([("a", "1.0.0", "1.1.0")], []))


if __name__ == "__main__":
    unittest.main()
