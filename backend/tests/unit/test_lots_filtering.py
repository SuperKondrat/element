from sqlalchemy.orm import Session

from app.models.enums import LotStatus
from app.models.lot import Lot
from app.models.lot_set import LotSet
from app.repositories import lots as lots_repo
from app.schemas.lot import LotFilter, SortDirection, SortField


def _make_set(db: Session) -> LotSet:
    lot_set = LotSet(name="test-set", lots_count=0, is_active=True)
    db.add(lot_set)
    db.flush()
    return lot_set


def _make_lot(db: Session, set_id: int, **overrides) -> Lot:
    external_id = f"ext-{overrides.pop('external_id', 'x')}"
    defaults = dict(
        external_id=external_id,
        set_id=set_id,
        project_name="ЖК Тест",
        address="г. Тест, ул. Тестовая, 1",
        rooms=1,
        area=40.0,
        floor=1,
        price=4_000_000,
        price_base=4_000_000,
        status=LotStatus.FOR_SALE,
    )
    defaults.update(overrides)
    lot = Lot(**defaults)
    db.add(lot)
    db.flush()
    return lot


def test_filters_by_project_name_case_insensitive_substring(db_session: Session):
    lot_set = _make_set(db_session)
    _make_lot(db_session, lot_set.id, external_id="a", project_name="ЖК Северный")
    _make_lot(db_session, lot_set.id, external_id="b", project_name="ЖК Южный")

    items, total = lots_repo.list_by_set(db_session, lot_set.id, LotFilter(project_name="северн"))

    assert total == 1
    assert items[0].project_name == "ЖК Северный"


def test_filters_by_rooms(db_session: Session):
    lot_set = _make_set(db_session)
    _make_lot(db_session, lot_set.id, external_id="a", rooms=1)
    _make_lot(db_session, lot_set.id, external_id="b", rooms=2)

    items, total = lots_repo.list_by_set(db_session, lot_set.id, LotFilter(rooms=2))

    assert total == 1
    assert items[0].rooms == 2


def test_filters_by_status(db_session: Session):
    lot_set = _make_set(db_session)
    _make_lot(db_session, lot_set.id, external_id="a", status=LotStatus.FOR_SALE)
    _make_lot(db_session, lot_set.id, external_id="b", status=LotStatus.SOLD)

    items, total = lots_repo.list_by_set(db_session, lot_set.id, LotFilter(status=LotStatus.SOLD))

    assert total == 1
    assert items[0].status == LotStatus.SOLD


def test_filters_by_price_per_sqm_range(db_session: Session):
    lot_set = _make_set(db_session)
    # price_per_sqm = 100_000
    _make_lot(db_session, lot_set.id, external_id="cheap", area=40.0, price=4_000_000)
    # price_per_sqm = 200_000
    _make_lot(db_session, lot_set.id, external_id="expensive", area=40.0, price=8_000_000)

    items, total = lots_repo.list_by_set(
        db_session, lot_set.id, LotFilter(price_per_sqm_min=150_000, price_per_sqm_max=250_000)
    )

    assert total == 1
    assert items[0].external_id == "ext-expensive"


def test_sorts_by_price_ascending(db_session: Session):
    lot_set = _make_set(db_session)
    _make_lot(db_session, lot_set.id, external_id="mid", price=5_000_000)
    _make_lot(db_session, lot_set.id, external_id="low", price=1_000_000)
    _make_lot(db_session, lot_set.id, external_id="high", price=9_000_000)

    items, _ = lots_repo.list_by_set(
        db_session, lot_set.id, LotFilter(sort_by=SortField.PRICE, sort_dir=SortDirection.ASC)
    )

    assert [item.external_id for item in items] == ["ext-low", "ext-mid", "ext-high"]


def test_sorts_by_area_descending(db_session: Session):
    lot_set = _make_set(db_session)
    _make_lot(db_session, lot_set.id, external_id="small", area=20.0)
    _make_lot(db_session, lot_set.id, external_id="big", area=90.0)

    items, _ = lots_repo.list_by_set(
        db_session, lot_set.id, LotFilter(sort_by=SortField.AREA, sort_dir=SortDirection.DESC)
    )

    assert [item.external_id for item in items] == ["ext-big", "ext-small"]


def test_pagination_splits_results_across_pages(db_session: Session):
    lot_set = _make_set(db_session)
    for i in range(5):
        _make_lot(db_session, lot_set.id, external_id=str(i), price=1_000_000 * (i + 1))

    page_1, total = lots_repo.list_by_set(
        db_session,
        lot_set.id,
        LotFilter(sort_by=SortField.PRICE, sort_dir=SortDirection.ASC, page=1, page_size=2),
    )
    page_2, _ = lots_repo.list_by_set(
        db_session,
        lot_set.id,
        LotFilter(sort_by=SortField.PRICE, sort_dir=SortDirection.ASC, page=2, page_size=2),
    )

    assert total == 5
    assert [item.external_id for item in page_1] == ["ext-0", "ext-1"]
    assert [item.external_id for item in page_2] == ["ext-2", "ext-3"]


def test_only_returns_lots_from_requested_set(db_session: Session):
    lot_set_a = _make_set(db_session)
    lot_set_b = _make_set(db_session)
    _make_lot(db_session, lot_set_a.id, external_id="a")
    _make_lot(db_session, lot_set_b.id, external_id="b")

    items, total = lots_repo.list_by_set(db_session, lot_set_a.id, LotFilter())

    assert total == 1
    assert items[0].external_id == "ext-a"
