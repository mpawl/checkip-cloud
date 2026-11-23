"""Check a running production image using only the Python standard library."""

import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def check_server(base_url):
    def request(path, expected=200, data=None, headers=None):
        req = Request(base_url + path, data=data, headers=headers or {})
        try:
            response = urlopen(req, timeout=5)
        except HTTPError as error:
            response = error
        with response:
            body = response.read().decode()
            assert response.status == expected, (path, response.status, body)
            return body

    deadline = time.monotonic() + 60
    while True:
        try:
            page = request("/")
            break
        except (URLError, TimeoutError):
            if time.monotonic() >= deadline:
                raise
            time.sleep(1)
    assert "Cloud IP Checker" in page

    for ip in ("104.16.0.1", "2606:4700::1"):
        result = json.loads(request("/api/ip/" + ip))
        assert result["ip"] == ip
        assert any(match["provider"] == "Cloudflare" for match in result["matches"])
        page = request("/", data=urlencode({"ip": ip}).encode())
        assert "Cloudflare" in page and ip in page

    for ip, status, message in (
        ("not-an-ip", 400, "not-an-ip is not a valid IP address."),
        ("192.0.2.10", 404, "192.0.2.10 not found."),
    ):
        assert json.loads(request("/api/ip/" + ip, expected=status)) == {"error": message}
        assert message in request("/", data=urlencode({"ip": ip}).encode())

    request("/", expected=422, data=b"", headers={"Content-Type": "application/x-www-form-urlencoded"})
    multipart = (
        '--checkip-boundary\r\nContent-Disposition: form-data; name="ip"\r\n'
        '\r\n104.16.0.1\r\n--checkip-boundary--\r\n'
    ).encode()
    assert "Cloudflare" in request(
        "/", data=multipart,
        headers={"Content-Type": "multipart/form-data; boundary=checkip-boundary"},
    )
    schema = json.loads(request("/openapi.json"))
    assert "/api/ip/{ip}" in schema["paths"]
    assert "post" in schema["paths"]["/"]
    print("Production smoke checks passed: UI, IPv4/IPv6, forms, errors, OpenAPI")


if __name__ == "__main__":
    check_server(sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000")
