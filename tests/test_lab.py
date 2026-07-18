"""Functional tests for the local Familiars Lab server."""

from __future__ import annotations

import json
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request

from familiars.cli import build_parser
from familiars.lab import create_server


class LabServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = create_server("127.0.0.1", 0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def fetch(self, path: str) -> tuple[bytes, dict[str, str]]:
        with urllib.request.urlopen(f"{self.base_url}{path}", timeout=5) as response:
            return response.read(), dict(response.headers.items())

    def post_recipe(self, recipe: object) -> tuple[int, dict[str, object]]:
        request = urllib.request.Request(
            f"{self.base_url}/api/validate-recipe",
            data=json.dumps(recipe).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read())

    def test_catalog_exposes_pets_states_packs_and_themes(self) -> None:
        payload, headers = self.fetch("/api/catalog")
        data = json.loads(payload)
        self.assertGreaterEqual(len(data["pets"]), 68)
        self.assertEqual(
            [state["id"] for state in data["states"]],
            [
                "idle",
                "running-right",
                "running-left",
                "waving",
                "jumping",
                "failed",
                "waiting",
                "running",
                "review",
            ],
        )
        self.assertIn("product-tropes", data["packs"])
        self.assertIn("familiars-dark", data["themes"])
        self.assertEqual(data["limits"]["petsPerScene"], 6)
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_static_ui_and_pet_atlas_are_served_locally(self) -> None:
        html, headers = self.fetch("/")
        javascript, _ = self.fetch("/app.js")
        spritesheet, sprite_headers = self.fetch("/pets/zentri/spritesheet.webp")
        self.assertIn(b"Familiars Lab", html)
        self.assertIn(b"/api/validate-recipe", javascript)
        self.assertNotIn(b"https://", html + javascript)
        self.assertTrue(spritesheet.startswith(b"RIFF"))
        self.assertEqual(sprite_headers["Content-Type"], "image/webp")
        self.assertIn("default-src 'self'", headers["Content-Security-Policy"])

    def test_valid_recipe_is_checked_by_the_real_renderer(self) -> None:
        status, result = self.post_recipe(
            {
                "version": 1,
                "title": "Test Council",
                "preset": "comparison",
                "theme": "familiars-dark",
                "outputs": {"formats": ["poster"], "dir": "output/sequences"},
                "scenes": [
                    {
                        "layout": "comparison",
                        "pets": [
                            {
                                "pet": "zentri",
                                "beats": [{"state": "review", "caption": "careful review"}],
                            },
                            {
                                "pet": "signal-surface",
                                "beats": [{"state": "running", "caption": "signal moving"}],
                            },
                        ],
                    }
                ],
            }
        )
        self.assertEqual(status, 200)
        self.assertEqual(result, {"ok": True, "title": "Test Council", "pets": 2, "scenes": 1})

    def test_invalid_recipe_is_rejected_without_writing(self) -> None:
        status, result = self.post_recipe(
            {
                "version": 1,
                "title": "Broken Council",
                "preset": "comparison",
                "theme": "familiars-dark",
                "outputs": {"formats": ["poster"], "dir": "output/sequences"},
                "scenes": [{"pets": ["not-a-familiar"]}],
            }
        )
        self.assertEqual(status, 400)
        self.assertFalse(result["ok"])
        self.assertIn("unknown pet id", str(result["error"]))

    def test_cross_origin_recipe_request_is_rejected(self) -> None:
        request = urllib.request.Request(
            f"{self.base_url}/api/validate-recipe",
            data=b"{}",
            headers={
                "Content-Type": "application/json",
                "Origin": "https://example.invalid",
                "Sec-Fetch-Site": "cross-site",
            },
            method="POST",
        )
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(request, timeout=5)
        self.assertEqual(caught.exception.code, 403)

    def test_download_endpoint_returns_a_validated_attachment(self) -> None:
        recipe = {
            "version": 1,
            "title": "Download Council",
            "preset": "spotlight",
            "theme": "familiars-dark",
            "outputs": {"formats": ["poster"], "dir": "output/sequences"},
            "scenes": [
                {
                    "pet": "zentri",
                    "beats": [{"state": "waving", "caption": "hello"}],
                }
            ],
        }
        request = urllib.request.Request(
            f"{self.base_url}/api/download-recipe",
            data=urllib.parse.urlencode({"recipe": json.dumps(recipe)}).encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            downloaded = json.loads(response.read())
            disposition = response.headers["Content-Disposition"]
        self.assertEqual(downloaded, recipe)
        self.assertEqual(disposition, 'attachment; filename="familiars-lab-council.json"')

    def test_unknown_pet_asset_is_not_served(self) -> None:
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.fetch("/pets/not-a-familiar/spritesheet.webp")
        self.assertEqual(caught.exception.code, 404)


class LabCliTests(unittest.TestCase):
    def test_lab_command_defaults_to_localhost(self) -> None:
        args = build_parser().parse_args(["lab", "--no-open"])
        self.assertEqual(args.host, "127.0.0.1")
        self.assertEqual(args.port, 8765)
        self.assertTrue(args.no_open)


if __name__ == "__main__":
    unittest.main()
