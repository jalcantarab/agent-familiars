#!/usr/bin/env python3
"""Check the release surface that normal validators do not cover."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "NOTICE.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "SUPPORT.md",
    "AGENTS.md",
    "assets/brand/familiars-banner.webp",
    "assets/brand/social-preview.png",
    "pyproject.toml",
    "setup.py",
    "MANIFEST.in",
    ".github/dependabot.yml",
    ".github/pull_request_template.md",
    ".github/workflows/validate.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/ISSUE_TEMPLATE/pet_polish.yml",
    ".github/ISSUE_TEMPLATE/pet_request.yml",
    "docs/CHOOSING_A_FAMILIAR.md",
    "docs/CLI.md",
    "docs/CREATE_A_PET.md",
    "docs/CREATE_A_REEL.md",
    "docs/CREATE_A_SEQUENCE.md",
    "docs/INSTALL.md",
    "docs/LICENSING.md",
    "docs/MAINTAINER_WORKFLOW.md",
    "docs/MCP.md",
    "docs/RELEASE.md",
]

README_LINKS = [
    "docs/INSTALL.md",
    "docs/CHOOSING_A_FAMILIAR.md",
    "docs/CLI.md",
    "docs/MCP.md",
    "docs/CREATE_A_PET.md",
    "docs/CREATE_A_SEQUENCE.md",
    "docs/RELEASE.md",
    "https://zentrik.ai",
]

TEXT_EXPECTATIONS = {
    "README.md": [
        "assets/brand/familiars-banner.webp",
        "curl -fsSL",
        "familiars render",
        "familiars-mcp",
        "Beyond required license notices, attribution is appreciated",
    ],
    "CHANGELOG.md": ["CLI", "MCP", "release-readiness"],
    "CONTRIBUTING.md": ["jab/<short-topic>", "scripts/check_release_readiness.py"],
    "AGENTS.md": ["jab/<short-topic>", "scripts/check_release_readiness.py"],
    "docs/MAINTAINER_WORKFLOW.md": ["Issue Triage", "pet-polish"],
    "docs/RELEASE.md": ["scripts/check_release_readiness.py", "Issue Intake"],
    ".github/workflows/validate.yml": ["Check release readiness"],
    ".github/pull_request_template.md": ["scripts/check_release_readiness.py"],
}

EXPECTED_PACK_COUNTS = {
    "first-50": 50,
    "product-tropes": 12,
    "state-instruments": 6,
}

EXPECTED_ISSUE_LABELS = {
    ".github/ISSUE_TEMPLATE/bug_report.yml": "labels: [bug]",
    ".github/ISSUE_TEMPLATE/feature_request.yml": "labels: [enhancement]",
    ".github/ISSUE_TEMPLATE/pet_polish.yml": "labels: [pet-polish]",
    ".github/ISSUE_TEMPLATE/pet_request.yml": "labels: [pet-request]",
}

FORBIDDEN_TRACKED_PARTS = {
    ".DS_Store",
    ".env",
    ".venv",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "output",
    "tmp",
}

FORBIDDEN_TEXT_SNIPPETS = [
    str(Path.home()),
]


def load_json(relative_path: str) -> object:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def check_required_files(failures: list[str]) -> None:
    for relative_path in REQUIRED_FILES:
        if not (ROOT / relative_path).is_file():
            fail(f"missing required public-release file: {relative_path}", failures)


def check_text_expectations(failures: list[str]) -> None:
    for relative_path, snippets in TEXT_EXPECTATIONS.items():
        path = ROOT / relative_path
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                fail(f"{relative_path} should mention {snippet!r}", failures)

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for link in README_LINKS:
        if link not in readme:
            fail(f"README.md should link to {link}", failures)


def check_issue_templates(failures: list[str]) -> None:
    for relative_path, label_line in EXPECTED_ISSUE_LABELS.items():
        path = ROOT / relative_path
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if label_line not in text:
            fail(f"{relative_path} should include {label_line}", failures)

    config = ROOT / ".github/ISSUE_TEMPLATE/config.yml"
    if config.is_file():
        text = config.read_text(encoding="utf-8")
        if "blank_issues_enabled: false" not in text:
            fail("issue template config should disable blank issues", failures)


def check_catalog_and_packs(failures: list[str]) -> None:
    pets = load_json("catalog/pets.json")
    packs = load_json("catalog/packs.json")
    if not isinstance(pets, list):
        fail("catalog/pets.json should be a list", failures)
        return
    if not isinstance(packs, dict):
        fail("catalog/packs.json should be an object", failures)
        return

    pet_ids = {pet.get("id") for pet in pets if isinstance(pet, dict)}
    if len(pet_ids) != len(pets):
        fail("catalog/pets.json should not contain duplicate or missing pet ids", failures)
    if len(pet_ids) < 50:
        fail(f"catalog should include at least 50 pets, found {len(pet_ids)}", failures)

    for pet in pets:
        if not isinstance(pet, dict):
            fail("catalog/pets.json contains a non-object pet entry", failures)
            continue
        pet_id = pet.get("id", "<missing>")
        folder_value = pet.get("folder")
        if not isinstance(folder_value, str):
            fail(f"{pet_id}: missing folder in catalog/pets.json", failures)
            continue
        folder = ROOT / folder_value
        for filename in ("pet.json", "spritesheet.webp", "README.md"):
            if not (folder / filename).is_file():
                fail(f"{pet_id}: missing {filename}", failures)

    for pack_id, expected_count in EXPECTED_PACK_COUNTS.items():
        pack = packs.get(pack_id)
        if not isinstance(pack, list):
            fail(f"catalog/packs.json missing list pack {pack_id}", failures)
            continue
        if len(pack) != expected_count:
            fail(f"{pack_id} should contain {expected_count} pets, found {len(pack)}", failures)
        if len(set(pack)) != len(pack):
            fail(f"{pack_id} should not contain duplicate pet ids", failures)

    for pack_id, pack in packs.items():
        if not isinstance(pack, list):
            fail(f"{pack_id} should be a list in catalog/packs.json", failures)
            continue
        missing = sorted(set(pack) - pet_ids)
        if missing:
            fail(f"{pack_id} references unknown pets: {', '.join(missing)}", failures)


def check_tracked_file_hygiene(failures: list[str]) -> None:
    for relative_path in tracked_files():
        parts = set(Path(relative_path).parts)
        if parts & FORBIDDEN_TRACKED_PARTS:
            fail(f"tracked local/build artifact should not be committed: {relative_path}", failures)
            continue

        path = ROOT / relative_path
        if not path.exists():
            continue
        if path.suffix.lower() in {".gif", ".jpg", ".jpeg", ".png", ".webp"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for snippet in FORBIDDEN_TEXT_SNIPPETS:
            if snippet in text:
                fail(f"{relative_path} contains local-only text: {snippet}", failures)


def main() -> None:
    failures: list[str] = []
    check_required_files(failures)
    check_text_expectations(failures)
    check_issue_templates(failures)
    check_catalog_and_packs(failures)
    check_tracked_file_hygiene(failures)

    if failures:
        for failure in failures:
            print(f"release readiness failed: {failure}", file=sys.stderr)
        raise SystemExit(1)

    print("release readiness ok")


if __name__ == "__main__":
    main()
