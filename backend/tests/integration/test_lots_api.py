import pytest
from fastapi.testclient import TestClient

from tests.helpers import TEST_ADMIN_PASSWORD, TEST_ADMIN_USERNAME, build_feed_xml, build_flat_xml


def _login(client: TestClient) -> str:
    response = client.post(
        "/api/auth/login", json={"username": TEST_ADMIN_USERNAME, "password": TEST_ADMIN_PASSWORD}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_login_rejects_wrong_password(client: TestClient):
    response = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401


def test_lots_list_empty_without_active_set(client: TestClient):
    response = client.get("/api/lots")
    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "page": 1, "page_size": 20}


def test_admin_routes_require_auth(client: TestClient):
    assert client.get("/api/admin/bookings").status_code == 401
    assert client.get("/api/admin/applications").status_code == 401
    assert client.get("/api/admin/lot-sets").status_code == 401


def test_full_public_flow(client: TestClient):
    token = _login(client)

    feed = build_feed_xml(
        build_flat_xml(flat_id="lot-a", status="FREE", room="1"),
        build_flat_xml(flat_id="lot-b", status="SOLD", room="2"),
    )
    upload = client.post(
        "/api/admin/lot-sets/upload",
        headers=_auth_headers(token),
        files={"file": ("feed.xml", feed, "application/xml")},
    )
    assert upload.status_code == 201, upload.text
    lot_set_id = upload.json()["id"]
    assert upload.json()["lots_count"] == 2

    # ещё не активен — витрина пустая
    assert client.get("/api/lots").json()["total"] == 0

    activate = client.post(f"/api/admin/lot-sets/{lot_set_id}/activate", headers=_auth_headers(token))
    assert activate.status_code == 200
    assert activate.json()["is_active"] is True

    listing = client.get("/api/lots", params={"status": "for_sale"})
    assert listing.status_code == 200
    body = listing.json()
    assert body["total"] == 1
    lot = body["items"][0]
    assert lot["external_id"] == "lot-a"
    assert lot["price_per_sqm"] == round(10_000_000 / 45.5, 2)

    booking = client.post(
        "/api/bookings",
        json={"lot_id": lot["id"], "contact_name": "Иван", "contact_phone": "+7 (999) 000-00-00"},
    )
    assert booking.status_code == 201
    assert booking.json()["status"] == "active"

    conflict = client.post(
        "/api/bookings",
        json={"lot_id": lot["id"], "contact_name": "Пётр", "contact_email": "petr@example.com"},
    )
    assert conflict.status_code == 409

    application = client.post(
        "/api/applications",
        json={"contact_name": "Мария", "contact_phone": "+7 (999) 111-22-33", "comment": "для семьи"},
    )
    assert application.status_code == 201
    assert application.json()["status"] == "new"

    admin_bookings = client.get("/api/admin/bookings", headers=_auth_headers(token))
    assert admin_bookings.status_code == 200
    assert len(admin_bookings.json()) == 1

    admin_applications = client.get("/api/admin/applications", headers=_auth_headers(token))
    assert admin_applications.status_code == 200
    assert len(admin_applications.json()) == 1


def test_booking_requires_phone_or_email(client: TestClient):
    response = client.post("/api/bookings", json={"lot_id": 1, "contact_name": "Иван"})
    assert response.status_code == 422


@pytest.mark.parametrize(
    "bad_params",
    [
        {"page_size": 101},  # выше верхней границы Field(le=100)
        {"page_size": 0},  # ниже нижней границы Field(ge=1)
        {"page": 0},  # ниже нижней границы Field(ge=1)
        {"sort_by": "not_a_field"},  # не входит в SortField
        {"status": "not_a_status"},  # не входит в LotStatus
    ],
)
def test_lots_list_rejects_invalid_filters_with_422(client: TestClient, bad_params: dict):
    """Регрессия на fc432a3: раньше LotFilter пересобирался вручную и
    ValidationError улетал в общий exception handler как 500 вместо 422."""
    response = client.get("/api/lots", params=bad_params)
    assert response.status_code == 422
