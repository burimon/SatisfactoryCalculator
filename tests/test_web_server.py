import http.client
import sys
import threading
import unittest
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from SatisfactoryCalculator.webapp.server import RecipeRequestHandler


@contextmanager
def running_server() -> Iterator[tuple[str, int]]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), RecipeRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        address = server.server_address
        host = str(address[0])
        port = int(address[1])
        yield host, port
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def request(host: str, port: int, method: str, path: str) -> tuple[int, str, bytes]:
    connection = http.client.HTTPConnection(host, port, timeout=5)
    connection.request(method, path)
    response = connection.getresponse()
    status = response.status
    content_type = response.getheader("Content-Type", "")
    body = response.read()
    connection.close()
    return status, content_type, body


class WebServerTests(unittest.TestCase):
    def test_root_serves_html_with_static_asset_references(self) -> None:
        with running_server() as (host, port):
            status, content_type, body = request(host, port, "GET", "/")

        self.assertEqual(status, 200)
        self.assertIn("text/html", content_type)
        html = body.decode("utf-8")
        self.assertIn("/static/css/base.css", html)
        self.assertIn("/static/js/app.js", html)
        self.assertIn('id="planner-net-balance"', html)

    def test_static_css_asset_is_served(self) -> None:
        with running_server() as (host, port):
            status, content_type, body = request(host, port, "GET", "/static/css/base.css")

        self.assertEqual(status, 200)
        self.assertIn("text/css", content_type)
        self.assertIn(":root {", body.decode("utf-8"))

    def test_static_js_asset_is_served(self) -> None:
        with running_server() as (host, port):
            status, content_type, body = request(host, port, "GET", "/static/js/app.js")

        self.assertEqual(status, 200)
        self.assertTrue("javascript" in content_type or "ecmascript" in content_type)
        self.assertIn("createPlannerController", body.decode("utf-8"))

    def test_static_path_traversal_is_rejected(self) -> None:
        with running_server() as (host, port):
            status, _, _ = request(host, port, "GET", "/static/%2e%2e/server.py")

        self.assertEqual(status, 400)


if __name__ == "__main__":
    unittest.main()
