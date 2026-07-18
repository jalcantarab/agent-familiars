"""Local browser playground for the packaged Familiars catalog."""

from __future__ import annotations

import json
import tempfile
import webbrowser
from functools import lru_cache
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit

from .pet_assets import (
    STATE_CAPTIONS,
    STATE_FRAME_COUNTS,
    STATE_INDEX,
    catalog,
    install_packs,
    spritesheet_path,
)
from .sequence_presets import profiles, themes
from .sequence_renderer import render_preview_frame
from .sequence_schema import normalize_recipe


LAB_ASSETS = Path(__file__).resolve().parent / "lab_assets"
MAX_REQUEST_BYTES = 64 * 1024
MAX_FORM_BYTES = 128 * 1024
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.css": ("app.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}


@lru_cache(maxsize=1)
def lab_catalog() -> dict[str, Any]:
    """Return the browser-safe metadata needed by the lab."""
    pack_data = install_packs()
    memberships: dict[str, list[str]] = {pet_id: [] for pet_id in catalog()}
    for pack_name, pet_ids in pack_data.items():
        for pet_id in pet_ids:
            memberships.setdefault(pet_id, []).append(pack_name)

    profile_data = profiles()
    pets = []
    for pet_id, entry in sorted(
        catalog().items(),
        key=lambda item: str(item[1].get("displayName", item[0])).lower(),
    ):
        profile = profile_data.get(pet_id, {})
        pets.append(
            {
                "id": pet_id,
                "displayName": entry.get("displayName", pet_id),
                "description": entry.get("description", ""),
                "subtitle": profile.get("subtitle", ""),
                "tags": entry.get("tags", []),
                "packs": sorted(memberships.get(pet_id, [])),
                "spritesheet": f"/pets/{pet_id}/spritesheet.webp",
            }
        )

    browser_themes = {}
    for name, theme in sorted(themes().items()):
        browser_themes[name] = {
            key: value
            for key, value in theme.items()
            if key in {"description", "background", "grid", "accent", "text", "muted", "card", "cardText"}
        }

    return {
        "pets": pets,
        "packs": pack_data,
        "states": [
            {
                "id": state,
                "caption": STATE_CAPTIONS[state],
                "frameCount": STATE_FRAME_COUNTS[state],
                "row": STATE_INDEX[state],
            }
            for state in STATE_INDEX
        ],
        "themes": browser_themes,
        "limits": {"petsPerScene": 6},
    }


class LabRequestHandler(BaseHTTPRequestHandler):
    """Serve the lab UI, pet atlases, and read-only recipe validation."""

    server_version = "FamiliarsLab/1"

    def version_string(self) -> str:
        return self.server_version

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path in STATIC_FILES:
            filename, content_type = STATIC_FILES[path]
            self._send_file(LAB_ASSETS / filename, content_type, cache="no-cache")
            return
        if path == "/api/catalog":
            self._send_json(HTTPStatus.OK, lab_catalog())
            return
        if path.startswith("/pets/") and path.endswith("/spritesheet.webp"):
            parts = Path(unquote(path)).parts
            if len(parts) != 4 or parts[1] != "pets" or parts[3] != "spritesheet.webp":
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            pet_id = parts[2]
            if pet_id not in catalog():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            self._send_file(
                spritesheet_path(pet_id),
                "image/webp",
                cache="public, max-age=3600",
            )
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_HEAD(self) -> None:
        path = urlsplit(self.path).path
        if path in STATIC_FILES:
            filename, content_type = STATIC_FILES[path]
            self._send_file(LAB_ASSETS / filename, content_type, cache="no-cache", head_only=True)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        if path not in {"/api/validate-recipe", "/api/download-recipe"}:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if not self._same_origin_request():
            self._send_json(HTTPStatus.FORBIDDEN, {"ok": False, "error": "cross-origin requests are not allowed"})
            return

        length = self.headers.get("Content-Length")
        if length is None:
            self._send_json(HTTPStatus.LENGTH_REQUIRED, {"ok": False, "error": "missing Content-Length"})
            return
        try:
            request_bytes = int(length)
        except ValueError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid Content-Length"})
            return
        limit = MAX_FORM_BYTES if path == "/api/download-recipe" else MAX_REQUEST_BYTES
        if request_bytes < 1 or request_bytes > limit:
            self._send_json(
                HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                {"ok": False, "error": f"request must be between 1 and {limit} bytes"},
            )
            return

        try:
            payload = self.rfile.read(request_bytes).decode("utf-8")
            if path == "/api/download-recipe":
                values = parse_qs(payload, strict_parsing=True)
                encoded_recipe = values.get("recipe", [None])[0]
                if encoded_recipe is None:
                    raise ValueError("download request missing recipe")
                raw = json.loads(encoded_recipe)
            else:
                raw = json.loads(payload)
            if not isinstance(raw, dict):
                raise ValueError("recipe must be a JSON object")
            recipe = normalize_recipe(
                raw,
                output_dir=Path(tempfile.gettempdir()) / "familiars-lab",
            )
            render_preview_frame(recipe)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
            return

        if path == "/api/download-recipe":
            self._send_download(
                "familiars-lab-council.json",
                f"{json.dumps(raw, indent=2)}\n".encode("utf-8"),
            )
            return

        self._send_json(
            HTTPStatus.OK,
            {
                "ok": True,
                "title": recipe["title"],
                "pets": sum(len(scene["pets"]) for scene in recipe["scenes"]),
                "scenes": len(recipe["scenes"]),
            },
        )

    def _send_download(self, filename: str, payload: bytes) -> None:
        self.send_response(HTTPStatus.OK)
        self._security_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _same_origin_request(self) -> bool:
        if self.headers.get("Sec-Fetch-Site") == "cross-site":
            return False
        origin = self.headers.get("Origin")
        if origin is None:
            return True
        host = self.headers.get("Host")
        parsed = urlsplit(origin)
        return parsed.scheme == "http" and bool(host) and parsed.netloc == host

    def _send_file(
        self,
        path: Path,
        content_type: str,
        *,
        cache: str,
        head_only: bool = False,
    ) -> None:
        try:
            payload = path.read_bytes()
        except FileNotFoundError:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self.send_response(HTTPStatus.OK)
        self._security_headers()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", cache)
        self.end_headers()
        if not head_only:
            self.wfile.write(payload)

    def _send_json(self, status: HTTPStatus, value: dict[str, Any]) -> None:
        payload = json.dumps(value, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self._security_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _security_headers(self) -> None:
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; "
            "style-src 'self'; script-src 'self'; connect-src 'self'; "
            "object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
        )
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")

    def log_message(self, format: str, *args: object) -> None:
        if getattr(self.server, "verbose", False):
            super().log_message(format, *args)


class LabServer(ThreadingHTTPServer):
    """Threaded local server with an optional request log."""

    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, server_address: tuple[str, int], *, verbose: bool = False):
        self.verbose = verbose
        super().__init__(server_address, LabRequestHandler)


def create_server(host: str, port: int, *, verbose: bool = False) -> LabServer:
    if not LAB_ASSETS.is_dir():
        raise RuntimeError(f"Familiars Lab assets are missing from {LAB_ASSETS}")
    return LabServer((host, port), verbose=verbose)


def run_lab(
    host: str = "127.0.0.1",
    port: int = 8765,
    *,
    open_browser: bool = True,
    verbose: bool = False,
) -> None:
    """Run the lab until interrupted."""
    server = create_server(host, port, verbose=verbose)
    actual_host, actual_port = server.server_address[:2]
    browser_host = "127.0.0.1" if actual_host in {"0.0.0.0", "::"} else actual_host
    url = f"http://{browser_host}:{actual_port}/"
    print(f"Familiars Lab is running at {url}")
    print("Press Ctrl-C to stop.")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Familiars Lab.")
    finally:
        server.server_close()
