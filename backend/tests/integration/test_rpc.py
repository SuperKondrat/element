import base64

from fastapi.testclient import TestClient

from tests.helpers import TEST_ADMIN_PASSWORD, TEST_ADMIN_USERNAME, build_feed_xml


def _rpc(client: TestClient, method: str, params: dict | None = None, call_id: int | None = 1, **headers):
    payload = {"jsonrpc": "2.0", "method": method, "params": params or {}}
    if call_id is not None:
        payload["id"] = call_id
    return client.post("/rpc", json=payload, headers=headers or None)


def _login_rpc(client: TestClient) -> str:
    response = _rpc(client, "auth.login", {"username": TEST_ADMIN_USERNAME, "password": TEST_ADMIN_PASSWORD})
    return response.json()["result"]["access_token"]


def test_rpc_login_success(client: TestClient):
    response = _rpc(client, "auth.login", {"username": TEST_ADMIN_USERNAME, "password": TEST_ADMIN_PASSWORD})
    assert response.status_code == 200
    body = response.json()
    assert body["jsonrpc"] == "2.0"
    assert body["id"] == 1
    assert "access_token" in body["result"]


def test_rpc_login_wrong_password_returns_domain_error_code(client: TestClient):
    response = _rpc(client, "auth.login", {"username": "admin", "password": "wrong"})
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == -32004


def test_rpc_unknown_method(client: TestClient):
    response = _rpc(client, "no.such.method")
    assert response.json()["error"]["code"] == -32601


def test_rpc_admin_method_requires_auth(client: TestClient):
    response = _rpc(client, "admin.bookings.list")
    assert response.json()["error"]["code"] == -32004


def test_rpc_notification_gets_no_response_body(client: TestClient):
    response = client.post("/rpc", json={"jsonrpc": "2.0", "method": "lots.list", "params": {}})
    assert response.status_code == 204


def test_rpc_batch_mixes_success_and_error(client: TestClient):
    payload = [
        {"jsonrpc": "2.0", "method": "lots.list", "params": {}, "id": 1},
        {"jsonrpc": "2.0", "method": "lots.get", "params": {"lot_id": 999999}, "id": 2},
    ]
    response = client.post("/rpc", json=payload)
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    assert "result" in results[0]
    assert results[1]["error"]["code"] == -32001


def test_rpc_feed_upload_activate_and_book(client: TestClient):
    token = _login_rpc(client)
    auth = {"Authorization": f"Bearer {token}"}

    feed_b64 = base64.b64encode(build_feed_xml()).decode()

    upload = _rpc(client, "admin.lot_sets.upload", {"filename": "feed.xml", "content_base64": feed_b64}, **auth)
    assert "result" in upload.json(), upload.text
    set_id = upload.json()["result"]["id"]

    activate = _rpc(client, "admin.lot_sets.activate", {"set_id": set_id}, **auth)
    assert activate.json()["result"]["is_active"] is True

    listing = _rpc(client, "lots.list", {})
    lot_id = listing.json()["result"]["items"][0]["id"]

    booking = _rpc(client, "bookings.create", {"lot_id": lot_id, "contact_name": "Иван", "contact_phone": "+7 (999) 000-00-00"})
    assert booking.json()["result"]["status"] == "active"

    conflict = _rpc(client, "bookings.create", {"lot_id": lot_id, "contact_name": "Пётр", "contact_email": "p@example.com"})
    assert conflict.json()["error"]["code"] == -32003
