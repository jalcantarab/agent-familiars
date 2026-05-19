#!/usr/bin/env python3
"""Validate animation design specs."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIRST_50_PATH = ROOT / "catalog" / "first-50-motion.json"
FLAGSHIP_PATH = ROOT / "catalog" / "flagship-10.json"
BRAND_SAFE_PATH = ROOT / "catalog" / "brand-safe-reference-lines.json"
PRODUCT_TROPE_PATH = ROOT / "catalog" / "product-trope-pets.json"

EXPECTED_STATES = [
    "idle",
    "running-right",
    "running-left",
    "waving",
    "jumping",
    "failed",
    "waiting",
    "running",
    "review",
]

FIRST_50_FIELDS = [
    "locomotion",
    "hoverOrJump",
    "workLoop",
    "waiting",
    "failed",
    "review",
]

REFERENCE_MOTION_FIELDS = [
    "locomotion",
    "jumping",
    "running",
    "waiting",
    "failed",
    "review",
]

FORBIDDEN_SNIPPETS = [
    "same as idle",
    "same animation",
    "generic jump",
    "generic wave",
    "jumps up and down",
    "waves hello",
    "looks sad",
    "does work",
    "working animation",
]


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict[str, object]:
    if not path.is_file():
        fail(f"missing {path.relative_to(ROOT)}")

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")


def require_string(value: object, label: str, min_chars: int) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a non-empty string")

    text = value.strip()
    if len(text) < min_chars:
        fail(f"{label} is too thin for production guidance: {text!r}")

    lowered = text.lower()
    for snippet in FORBIDDEN_SNIPPETS:
        if snippet in lowered:
            fail(f"{label} contains placeholder motion language: {snippet!r}")

    return text


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def require_rank_sequence(pets: list[object], expected_count: int, label: str) -> list[dict[str, object]]:
    if len(pets) != expected_count:
        fail(f"{label} must contain exactly {expected_count} pets, found {len(pets)}")

    typed_pets = []
    ranks = []
    ids = []
    for index, pet in enumerate(pets, start=1):
        if not isinstance(pet, dict):
            fail(f"{label}[{index}] must be an object")
        typed_pets.append(pet)
        ranks.append(pet.get("rank"))
        ids.append(pet.get("id"))

    expected_ranks = list(range(1, expected_count + 1))
    if ranks != expected_ranks:
        fail(f"{label} ranks must be {expected_ranks}, found {ranks}")

    if any(not isinstance(pet_id, str) or not pet_id.strip() for pet_id in ids):
        fail(f"{label} contains a missing or empty id")

    if len(set(ids)) != len(ids):
        fail(f"{label} contains duplicate ids")

    return typed_pets


def validate_first_50() -> tuple[dict[str, object], set[str]]:
    data = load_json(FIRST_50_PATH)

    if data.get("schemaVersion") != 1:
        fail("catalog/first-50-motion.json schemaVersion must be 1")

    fields = data.get("fields")
    if fields != FIRST_50_FIELDS:
        fail(f"catalog/first-50-motion.json fields must be {FIRST_50_FIELDS}")

    pets = data.get("pets")
    if not isinstance(pets, list):
        fail("catalog/first-50-motion.json pets must be an array")

    typed_pets = require_rank_sequence(pets, 50, "catalog/first-50-motion.json pets")
    ids: set[str] = set()

    for pet in typed_pets:
        pet_id = require_string(pet.get("id"), f"first-50 rank {pet.get('rank')} id", 2)
        ids.add(pet_id)
        require_string(pet.get("name"), f"{pet_id}.name", 3)
        require_string(pet.get("archetype"), f"{pet_id}.archetype", 10)

        motion_values = []
        for field in FIRST_50_FIELDS:
            motion_values.append(require_string(pet.get(field), f"{pet_id}.{field}", 34))

        normalized = [normalize(value) for value in motion_values]
        if len(set(normalized)) != len(normalized):
            fail(f"{pet_id} repeats a motion description across first-50 fields")

    return data, ids


def validate_flagship(first_50_ids: set[str]) -> dict[str, object]:
    data = load_json(FLAGSHIP_PATH)

    if data.get("schemaVersion") != 1:
        fail("catalog/flagship-10.json schemaVersion must be 1")

    if data.get("states") != EXPECTED_STATES:
        fail(f"catalog/flagship-10.json states must be {EXPECTED_STATES}")

    require_string(data.get("selectionPrinciple"), "flagship selectionPrinciple", 80)

    pets = data.get("pets")
    if not isinstance(pets, list):
        fail("catalog/flagship-10.json pets must be an array")

    typed_pets = require_rank_sequence(pets, 10, "catalog/flagship-10.json pets")

    for pet in typed_pets:
        rank = pet.get("rank")
        pet_id = require_string(pet.get("id"), f"flagship rank {rank} id", 2)
        if pet_id not in first_50_ids:
            fail(f"flagship pet {pet_id!r} does not exist in first-50 motion specs")

        require_string(pet.get("displayName"), f"{pet_id}.displayName", 3)
        require_string(pet.get("status"), f"{pet_id}.status", 6)

        for field in ("whyFlagship", "audienceMoment", "characterCore", "visualLock"):
            require_string(pet.get(field), f"{pet_id}.{field}", 50)

        principles = pet.get("animationPrinciples")
        if not isinstance(principles, list) or len(principles) < 3:
            fail(f"{pet_id}.animationPrinciples must contain at least three principles")

        for index, principle in enumerate(principles, start=1):
            require_string(principle, f"{pet_id}.animationPrinciples[{index}]", 35)

        state_animations = pet.get("stateAnimations")
        if not isinstance(state_animations, dict):
            fail(f"{pet_id}.stateAnimations must be an object")

        if list(state_animations.keys()) != EXPECTED_STATES:
            fail(f"{pet_id}.stateAnimations must define the nine Codex states in order")

        descriptions = []
        for state in EXPECTED_STATES:
            descriptions.append(require_string(state_animations.get(state), f"{pet_id}.{state}", 50))

        normalized = [normalize(description) for description in descriptions]
        if len(set(normalized)) != len(normalized):
            fail(f"{pet_id} repeats a state animation description")

    return data


def validate_brand_safe_reference_lines() -> dict[str, object]:
    data = load_json(BRAND_SAFE_PATH)

    if data.get("schemaVersion") != 1:
        fail("catalog/brand-safe-reference-lines.json schemaVersion must be 1")

    for field in ("description", "selectionPrinciple"):
        require_string(data.get(field), f"brand-safe {field}", 80)

    brand_safety_rules = data.get("brandSafetyRules")
    if not isinstance(brand_safety_rules, list) or len(brand_safety_rules) < 5:
        fail("brandSafetyRules must contain at least five rules")
    for index, rule in enumerate(brand_safety_rules, start=1):
        require_string(rule, f"brandSafetyRules[{index}]", 35)

    first_production = data.get("firstProductionTwelve")
    if not isinstance(first_production, list) or len(first_production) != 12:
        fail("firstProductionTwelve must contain exactly 12 ids")
    if any(not isinstance(pet_id, str) or not pet_id.strip() for pet_id in first_production):
        fail("firstProductionTwelve contains a missing or empty id")
    if len(set(first_production)) != len(first_production):
        fail("firstProductionTwelve contains duplicate ids")

    lines = data.get("lines")
    if not isinstance(lines, list):
        fail("catalog/brand-safe-reference-lines.json lines must be an array")

    typed_lines = require_rank_sequence(lines, 30, "catalog/brand-safe-reference-lines.json lines")
    line_ids: set[str] = set()

    for line in typed_lines:
        rank = line.get("rank")
        line_id = require_string(line.get("id"), f"brand-safe rank {rank} id", 2)
        line_ids.add(line_id)

        for field in (
            "displayName",
            "status",
            "audienceWorkflow",
            "whyItLands",
            "brandSafetyGuardrails",
            "visualLock",
        ):
            if field in {"displayName", "status"}:
                min_chars = 6
            elif field == "audienceWorkflow":
                min_chars = 30
            else:
                min_chars = 45
            require_string(line.get(field), f"{line_id}.{field}", min_chars)

        motion_signature = line.get("motionSignature")
        if not isinstance(motion_signature, dict):
            fail(f"{line_id}.motionSignature must be an object")

        if list(motion_signature.keys()) != REFERENCE_MOTION_FIELDS:
            fail(f"{line_id}.motionSignature must define {REFERENCE_MOTION_FIELDS} in order")

        descriptions = []
        for field in REFERENCE_MOTION_FIELDS:
            descriptions.append(
                require_string(motion_signature.get(field), f"{line_id}.motionSignature.{field}", 34)
            )

        normalized = [normalize(description) for description in descriptions]
        if len(set(normalized)) != len(normalized):
            fail(f"{line_id} repeats a reference-line motion description")

    missing = sorted(set(first_production) - line_ids)
    if missing:
        fail(f"firstProductionTwelve references missing ids: {missing}")

    return data


def validate_product_trope_pets() -> dict[str, object]:
    data = load_json(PRODUCT_TROPE_PATH)

    if data.get("schemaVersion") != 1:
        fail("catalog/product-trope-pets.json schemaVersion must be 1")

    if data.get("states") != EXPECTED_STATES:
        fail(f"catalog/product-trope-pets.json states must be {EXPECTED_STATES}")

    for field in ("description", "selectionPrinciple"):
        require_string(data.get(field), f"product-trope {field}", 80)

    production_rules = data.get("productionRules")
    if not isinstance(production_rules, list) or len(production_rules) < 5:
        fail("product trope productionRules must contain at least five rules")
    for index, rule in enumerate(production_rules, start=1):
        require_string(rule, f"productTropes.productionRules[{index}]", 45)

    first_production = data.get("firstProductionSix")
    if not isinstance(first_production, list) or len(first_production) != 6:
        fail("firstProductionSix must contain exactly six ids")
    if any(not isinstance(pet_id, str) or not pet_id.strip() for pet_id in first_production):
        fail("firstProductionSix contains a missing or empty id")
    if len(set(first_production)) != len(first_production):
        fail("firstProductionSix contains duplicate ids")

    pets = data.get("pets")
    if not isinstance(pets, list):
        fail("catalog/product-trope-pets.json pets must be an array")

    typed_pets = require_rank_sequence(pets, 12, "catalog/product-trope-pets.json pets")
    pet_ids: set[str] = set()

    for pet in typed_pets:
        rank = pet.get("rank")
        pet_id = require_string(pet.get("id"), f"product-trope rank {rank} id", 2)
        pet_ids.add(pet_id)

        for field in ("displayName", "trope", "personality", "stateCarrier", "visualLock"):
            min_chars = 6 if field == "displayName" else 55
            require_string(pet.get(field), f"{pet_id}.{field}", min_chars)

        event_feel = pet.get("eventFeel")
        if not isinstance(event_feel, dict):
            fail(f"{pet_id}.eventFeel must be an object")
        if list(event_feel.keys()) != EXPECTED_STATES:
            fail(f"{pet_id}.eventFeel must define the nine Codex states in order")

        animations = []
        user_feelings = []
        for state in EXPECTED_STATES:
            state_spec = event_feel.get(state)
            if not isinstance(state_spec, dict):
                fail(f"{pet_id}.eventFeel.{state} must be an object")
            user_feelings.append(
                require_string(state_spec.get("userFeeling"), f"{pet_id}.{state}.userFeeling", 29)
            )
            animations.append(
                require_string(state_spec.get("animation"), f"{pet_id}.{state}.animation", 50)
            )
            require_string(state_spec.get("qaFocus"), f"{pet_id}.{state}.qaFocus", 12)

        normalized_animations = [normalize(animation) for animation in animations]
        if len(set(normalized_animations)) != len(normalized_animations):
            fail(f"{pet_id} repeats a product-trope state animation")

        normalized_feelings = [normalize(feeling) for feeling in user_feelings]
        if len(set(normalized_feelings)) != len(normalized_feelings):
            fail(f"{pet_id} repeats a product-trope user feeling")

    missing = sorted(set(first_production) - pet_ids)
    if missing:
        fail(f"firstProductionSix references missing ids: {missing}")

    return data


def main() -> None:
    first_50, first_50_ids = validate_first_50()
    flagship = validate_flagship(first_50_ids)
    brand_safe = validate_brand_safe_reference_lines()
    product_tropes = validate_product_trope_pets()

    print(
        json.dumps(
            {
                "ok": True,
                "first50Pets": len(first_50["pets"]),
                "flagshipPets": len(flagship["pets"]),
                "brandSafeReferenceLines": len(brand_safe["lines"]),
                "productTropePets": len(product_tropes["pets"]),
                "statesPerFlagship": len(EXPECTED_STATES),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
