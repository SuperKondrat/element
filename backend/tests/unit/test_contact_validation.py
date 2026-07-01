import pytest
from pydantic import ValidationError

from app.schemas.booking import BookingCreate

VALID_PHONE = "+7 (999) 123-45-67"
VALID_EMAIL = "buyer@example.com"


def test_accepts_valid_phone_and_email():
    data = BookingCreate(lot_id=1, contact_name="Иван", contact_phone=VALID_PHONE, contact_email=VALID_EMAIL)
    assert data.contact_phone == VALID_PHONE
    assert data.contact_email == VALID_EMAIL


@pytest.mark.parametrize(
    "bad_phone",
    [
        "+79991234567",  # без маски
        "89991234567",  # без маски, с 8
        "+7 999 123 45 67",  # без скобок/дефисов
        "+7 (999) 123-45",  # неполный номер
        "не телефон",
    ],
)
def test_rejects_malformed_phone(bad_phone):
    with pytest.raises(ValidationError):
        BookingCreate(lot_id=1, contact_name="Иван", contact_phone=bad_phone)


@pytest.mark.parametrize(
    "bad_email",
    ["не почта", "buyer@", "@example.com", "buyer@example", "buyer example.com"],
)
def test_rejects_malformed_email(bad_email):
    with pytest.raises(ValidationError):
        BookingCreate(lot_id=1, contact_name="Иван", contact_email=bad_email)


def test_requires_at_least_one_contact_method():
    with pytest.raises(ValidationError):
        BookingCreate(lot_id=1, contact_name="Иван")
