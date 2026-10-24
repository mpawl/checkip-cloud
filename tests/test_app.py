from fastapi.testclient import TestClient

from app import main


client = TestClient(main.app)
MATCH = {
    "provider": "Example Cloud",
    "cidr": "192.0.2.0/24",
    "service": "Test",
}


def stub_checker(monkeypatch):
    monkeypatch.setattr(main.checker, "is_ip_address", lambda value: value == "192.0.2.10")
    monkeypatch.setattr(main.checker, "lookup_ip", lambda value: [MATCH])


def test_home_page_renders():
    response = client.get("/")

    assert response.status_code == 200
    assert "Cloud IP Checker" in response.text


def test_api_returns_matches(monkeypatch):
    stub_checker(monkeypatch)

    response = client.get("/api/ip/192.0.2.10")

    assert response.status_code == 200
    assert response.json() == {"ip": "192.0.2.10", "matches": [MATCH]}


def test_api_rejects_invalid_ip(monkeypatch):
    stub_checker(monkeypatch)

    response = client.get("/api/ip/not-an-ip")

    assert response.status_code == 400
    assert response.json() == {"error": "not-an-ip is not a valid IP address."}


def test_form_submission_renders_matches(monkeypatch):
    stub_checker(monkeypatch)

    response = client.post("/", data={"ip": "192.0.2.10"})

    assert response.status_code == 200
    assert "Example Cloud" in response.text
    assert "192.0.2.0/24" in response.text


def test_form_submission_reports_invalid_ip(monkeypatch):
    stub_checker(monkeypatch)

    response = client.post("/", data={"ip": "not-an-ip"})

    assert response.status_code == 200
    assert "not-an-ip is not a valid IP address." in response.text
