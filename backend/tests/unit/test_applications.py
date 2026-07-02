import pytest
from sqlalchemy.orm import Session

from app.models.enums import LotStatus
from app.models.lot import Lot
from app.models.lot_set import LotSet
from app.schemas.application import ApplicationCreate
from app.services import applications as applications_service
from app.services.exceptions import LotNotFoundError


def _make_lot(db: Session) -> Lot:
    lot_set = LotSet(name="test-set", lots_count=1, is_active=True)
    db.add(lot_set)
    db.flush()

    lot = Lot(
        external_id="ext-1",
        set_id=lot_set.id,
        project_name="ЖК Тест",
        address="г. Тест, ул. Тестовая, 1",
        rooms=2,
        area=45.5,
        floor=3,
        price=10_000_000,
        price_base=11_000_000,
        status=LotStatus.FOR_SALE,
    )
    db.add(lot)
    db.flush()
    return lot


def test_creates_general_application_without_lot(db_session: Session):
    application = applications_service.create_application(
        db_session,
        ApplicationCreate(contact_name="Мария", contact_phone="+7 (999) 111-22-33"),
    )

    assert application.lot_id is None
    assert application.status.value == "new"


def test_creates_application_tied_to_existing_lot(db_session: Session):
    lot = _make_lot(db_session)

    application = applications_service.create_application(
        db_session,
        ApplicationCreate(lot_id=lot.id, contact_name="Мария", contact_email="maria@example.com"),
    )

    assert application.lot_id == lot.id


def test_application_for_unknown_lot_raises_not_found(db_session: Session):
    with pytest.raises(LotNotFoundError):
        applications_service.create_application(
            db_session,
            ApplicationCreate(lot_id=999_999, contact_name="Мария", contact_phone="+7 (999) 111-22-33"),
        )


def test_list_applications_returns_created_ones(db_session: Session):
    applications_service.create_application(
        db_session,
        ApplicationCreate(contact_name="Мария", contact_phone="+7 (999) 111-22-33"),
    )
    applications_service.create_application(
        db_session,
        ApplicationCreate(contact_name="Пётр", contact_email="petr@example.com"),
    )

    result = applications_service.list_applications(db_session)

    assert len(result) == 2
