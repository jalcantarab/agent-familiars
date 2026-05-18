"""Package build customizations for Familiars."""

from __future__ import annotations

from pathlib import Path
from shutil import copy2, copytree, rmtree

from setuptools import setup
from setuptools.command.build_py import build_py as build_py_base


ROOT = Path(__file__).resolve().parent


class build_py(build_py_base):
    """Copy the runtime data bundle without README preview media."""

    def run(self) -> None:
        super().run()
        self.copy_runtime_bundle()

    def copy_runtime_bundle(self) -> None:
        target = Path(self.build_lib) / "familiars" / "_bundle"
        if target.exists():
            rmtree(target)
        target.mkdir(parents=True)

        for folder in ("catalog", "docs", "examples", "licenses"):
            copytree(ROOT / folder, target / folder)
        copytree(ROOT / "assets" / "brand", target / "assets" / "brand")

        for filename in ("LICENSE", "NOTICE.md"):
            copy2(ROOT / filename, target / filename)

        pets_target = target / "pets"
        pets_target.mkdir()
        for source_dir in sorted((ROOT / "pets").iterdir()):
            if not source_dir.is_dir():
                continue
            pet_target = pets_target / source_dir.name
            pet_target.mkdir()
            for filename in ("pet.json", "spritesheet.webp"):
                copy2(source_dir / filename, pet_target / filename)


setup(cmdclass={"build_py": build_py})
