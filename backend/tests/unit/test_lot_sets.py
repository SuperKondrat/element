import pytest
from sqlalchemy.orm import Session

from app.repositories import lot_sets as lot_sets_repo
from app.services import lot_sets as lot_sets_service
from app.services.exceptions import LotSetNotFoundError


def test_activate_unknown_set_raises_not_found(db_session: Session):
    with pytest.raises(LotSetNotFoundError):
        lot_sets_service.activate_set(db_session, 999_999)


def test_activating_a_set_deactivates_the_previous_one(db_session: Session):
    first = lot_sets_repo.create(db_session, name="first.xml", lots_count=0)
    second = lot_sets_repo.create(db_session, name="second.xml", lots_count=0)
    db_session.flush()

    lot_sets_service.activate_set(db_session, first.id)
    assert lot_sets_repo.get_active(db_session).id == first.id

    lot_sets_service.activate_set(db_session, second.id)

    active = lot_sets_repo.get_active(db_session)
    assert active.id == second.id
    db_session.refresh(first)
    assert first.is_active is False


def test_new_upload_is_not_active_by_default(db_session: Session):
    lot_set = lot_sets_repo.create(db_session, name="feed.xml", lots_count=0)
    db_session.flush()

    assert lot_set.is_active is False
    assert lot_sets_repo.get_active(db_session) is None
