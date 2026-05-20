#!/usr/bin/env python3
"""Validate Markdown links, embedded assets, and README image weight."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE_EXTENSIONS = {".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}
DEFAULT_README_IMAGE_BUDGET = 6_000_000
README_CHOOSER_CARDS = {
    "assets/readme/signal-heron.gif",
    "assets/readme/merge-mammoth.gif",
    "assets/readme/signal-surface.gif",
    "assets/readme/no-knight.gif",
    "assets/readme/ci-phoenix.gif",
    "assets/readme/intent-compass.gif",
}
README_PRIMARY_REEL = "assets/showcase/familiars-reel.gif"


def iter_markdown_files() -> list[Path]:
    ignored_parts = {
        ".git",
        ".venv",
        "build",
        "dist",
        "node_modules",
        "__pycache__",
    }
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if not ignored_parts.intersection(path.relative_to(ROOT).parts)
        and not any(part.endswith(".egg-info") for part in path.relative_to(ROOT).parts)
    )


def normalize_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]
    return target.split()[0].strip("<>")


def is_external(target: str) -> bool:
    return (
        "://" in target
        or target.startswith("#")
        or target.startswith("mailto:")
        or target.startswith("tel:")
    )


def referenced_paths(markdown_path: Path) -> list[tuple[str, Path, bool, bool]]:
    text = markdown_path.read_text(encoding="utf-8")
    refs: list[tuple[str, Path, bool, bool]] = []

    for match in re.finditer(r"!?\[[^\]]*\]\(([^)]+)\)", text):
        target = normalize_target(match.group(1))
        if is_external(target):
            continue
        path_part = target.split("#", 1)[0]
        if not path_part:
            continue
        resolved = (markdown_path.parent / path_part).resolve()
        matched = match.group(0)
        is_image = resolved.suffix.lower() in IMAGE_EXTENSIONS
        is_embedded = matched.startswith("!") or matched.startswith("[![")
        refs.append((target, resolved, is_image, is_embedded))

    for attribute in ("src", "href"):
        for match in re.finditer(attribute + r"=[\"']([^\"']+)[\"']", text):
            target = match.group(1).strip()
            if is_external(target):
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            resolved = (markdown_path.parent / path_part).resolve()
            refs.append(
                (
                    target,
                    resolved,
                    resolved.suffix.lower() in IMAGE_EXTENSIONS,
                    attribute == "src",
                )
            )

    return refs


def validate_links(markdown_files: list[Path]) -> int:
    missing: list[str] = []
    for markdown_path in markdown_files:
        for target, resolved, _, _ in referenced_paths(markdown_path):
            if not resolved.exists():
                missing.append(f"{markdown_path.relative_to(ROOT)}: missing {target}")

    if missing:
        for message in missing:
            print(message, file=sys.stderr)
        return 1
    return 0


def validate_readme_weight(budget: int) -> int:
    readme = ROOT / "README.md"
    total = 0
    images: list[tuple[str, int]] = []
    for target, resolved, is_image, is_embedded in referenced_paths(readme):
        if is_image and is_embedded and resolved.exists():
            size = resolved.stat().st_size
            images.append((target, size))
            total += size

    if total > budget:
        print(
            f"README image references total {total:,} bytes, over budget {budget:,} bytes",
            file=sys.stderr,
        )
        for target, size in sorted(images, key=lambda item: item[1], reverse=True):
            print(f"  {target}: {size:,} bytes", file=sys.stderr)
        return 1

    print(
        f"docs ok: {len(iter_markdown_files())} markdown files, README images {total:,}/{budget:,} bytes"
    )
    return 0


def validate_readme_chooser_media() -> int:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    start = text.find("## Pick A Familiar")
    if start == -1:
        print("README.md: missing Pick A Familiar section", file=sys.stderr)
        return 1
    end = text.find("\n## ", start + 1)
    section = text[start:] if end == -1 else text[start:end]

    srcs = set(re.findall(r"src=[\"']([^\"']+)[\"']", section))
    if srcs != README_CHOOSER_CARDS:
        print(
            "README.md: Pick A Familiar must use the six uniform animated assets/readme cards",
            file=sys.stderr,
        )
        missing = sorted(README_CHOOSER_CARDS - srcs)
        extra = sorted(srcs - README_CHOOSER_CARDS)
        for target in missing:
            print(f"  missing {target}", file=sys.stderr)
        for target in extra:
            print(f"  unexpected {target}", file=sys.stderr)
        return 1

    return 0


def validate_readme_primary_reel() -> int:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    if f"]({README_PRIMARY_REEL})" not in text:
        print(
            f"README.md: primary showcase should embed {README_PRIMARY_REEL}",
            file=sys.stderr,
        )
        return 1
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--readme-image-budget",
        type=int,
        default=DEFAULT_README_IMAGE_BUDGET,
        help="Maximum total bytes for embedded local image references in README.md.",
    )
    args = parser.parse_args()

    markdown_files = iter_markdown_files()
    exit_code = validate_links(markdown_files)
    if exit_code == 0:
        exit_code = validate_readme_chooser_media()
    if exit_code == 0:
        exit_code = validate_readme_primary_reel()
    if exit_code == 0:
        exit_code = validate_readme_weight(args.readme_image_budget)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
