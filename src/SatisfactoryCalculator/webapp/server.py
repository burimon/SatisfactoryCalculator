from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

from .api import find_recipe_payloads_by_output, get_recipe_payload, list_items, list_recipes
from .index_html import HTML


class RecipeRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        try:
            if self.path in {"/", "/index.html"}:
                self._write_html(HTML)
                return
            if self.path == "/api/recipes":
                self._write_json(list_recipes())
                return
            if self.path == "/api/items":
                self._write_json(list_items())
                return
            if self.path.startswith("/api/recipes/by-output/"):
                item_id = unquote(self.path.removeprefix("/api/recipes/by-output/"))
                self._write_json(find_recipe_payloads_by_output(item_id))
                return
            if self.path.startswith("/api/recipes/"):
                recipe_id = unquote(self.path.removeprefix("/api/recipes/"))
                self._write_json(get_recipe_payload(recipe_id))
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
        except KeyError as exc:
            self.send_error(HTTPStatus.NOT_FOUND, str(exc))
        except ValueError as exc:
            self.send_error(HTTPStatus.BAD_REQUEST, str(exc))

    def log_message(self, format: str, *args: object) -> None:
        return

    def _write_html(self, content: str) -> None:
        data = content.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _write_json(self, payload: object) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run_web_app(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), RecipeRequestHandler)
    print(f"Satisfactory Recipe Browser running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
