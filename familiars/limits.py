"""Shared safety limits for Familiars rendering surfaces."""

from __future__ import annotations

from .pet_assets import ROOT


DEFAULT_OUTPUT_ROOT = ROOT / "output" / "sequences"
ALLOWED_OUTPUT_FORMATS = {"gif", "mp4", "poster"}
ALLOWED_LAYOUTS = {"spotlight", "comparison"}
MAX_WIDTH = 1920
MAX_HEIGHT = 1080
MAX_PIXELS = MAX_WIDTH * MAX_HEIGHT
MAX_FPS = 30
MAX_BEAT_SECONDS = 10.0
MAX_SCENES = 12
MAX_PETS_PER_SCENE = 8
MAX_TOTAL_FRAMES = 1800
