from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

from .api import (
    find_recipe_payloads_by_output,
    get_recipe_payload,
    get_workflow_payload,
    list_items,
    list_recipes,
    list_workflows,
    save_workflow,
)
from .static_assets import static_asset_bytes, static_asset_content_type


class RecipeRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        try:
            request_path = self._request_path()
            if request_path in {"/", "/index.html"}:
                self._write_static("index.html")
                return
            if request_path.startswith("/static/"):
                asset_path = unquote(request_path.removeprefix("/static/"))
                self._write_static(asset_path)
                return
            if request_path == "/api/recipes":
                self._write_json(list_recipes())
                return
            if request_path == "/api/items":
                self._write_json(list_items())
                return
            if request_path == "/api/workflows":
                self._write_json(list_workflows())
                return
            if request_path.startswith("/api/workflows/"):
                filename = unquote(request_path.removeprefix("/api/workflows/"))
                self._write_json(get_workflow_payload(filename))
                return
            if request_path.startswith("/api/recipes/by-output/"):
                item_id = unquote(request_path.removeprefix("/api/recipes/by-output/"))
                self._write_json(find_recipe_payloads_by_output(item_id))
                return
            if request_path.startswith("/api/recipes/"):
                recipe_id = unquote(request_path.removeprefix("/api/recipes/"))
                self._write_json(get_recipe_payload(recipe_id))
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
        except KeyError as exc:
            self.send_error(HTTPStatus.NOT_FOUND, str(exc))
        except FileNotFoundError as exc:
            self.send_error(HTTPStatus.NOT_FOUND, str(exc))
        except ValueError as exc:
            self.send_error(HTTPStatus.BAD_REQUEST, str(exc))

    def do_POST(self) -> None:
        try:
            if self._request_path() == "/api/workflows":
                content_length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                if not isinstance(payload, dict):
                    raise ValueError("Workflow payload must be an object")
                self._write_json(save_workflow(payload))
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
        except FileNotFoundError as exc:
            self.send_error(HTTPStatus.NOT_FOUND, str(exc))
        except ValueError as exc:
            self.send_error(HTTPStatus.BAD_REQUEST, str(exc))

    def log_message(self, format: str, *args: object) -> None:
        return

    def _request_path(self) -> str:
        return urlparse(self.path).path

    def _write_static(self, asset_path: str) -> None:
        data = static_asset_bytes(asset_path)
        content_type = static_asset_content_type(asset_path)
        if content_type.startswith("text/") or content_type in {
            "application/javascript",
            "text/javascript",
            "application/json",
        }:
            content_type = f"{content_type}; charset=utf-8"
        self._write_bytes(content_type, data)

    def _write_bytes(self, content_type: str, data: bytes) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _write_json(self, payload: object) -> None:
        data = json.dumps(payload).encode("utf-8")
        self._write_bytes("application/json; charset=utf-8", data)


def run_web_app(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), RecipeRequestHandler)
    print(f"Satisfactory Recipe Browser running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
