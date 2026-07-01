from pathlib import Path

import pytest

from app.models.enums import LotStatus
from app.services.feed_parser import FeedParseError, parse_feed
from tests.helpers import build_feed_xml as _feed
from tests.helpers import build_flat_xml as _flat

FEED_ROOT = Path(__file__).resolve().parents[3] / "feeds" / "element.xml"


def test_parses_flat_fields_and_maps_status():
    result = parse_feed(_feed(_flat(flat_id="abc", status="RESERVED", room="0", area="24.08")))

    assert result.skipped_count == 0
    assert len(result.lots) == 1

    lot = result.lots[0]
    assert lot.external_id == "abc"
    assert lot.project_name == "ЖК Тест"
    assert lot.address == "г. Тест, ул. Тестовая, 1"
    assert lot.rooms == 0
    assert lot.area == 24.08
    assert lot.floor == 5
    assert lot.price == 10000000
    assert lot.price_base == 11000000
    assert lot.status == LotStatus.RESERVED


@pytest.mark.parametrize(
    ("raw_status", "expected"),
    [("FREE", LotStatus.FOR_SALE), ("RESERVED", LotStatus.RESERVED), ("SOLD", LotStatus.SOLD)],
)
def test_status_mapping(raw_status, expected):
    result = parse_feed(_feed(_flat(status=raw_status)))
    assert result.lots[0].status == expected


def test_skips_flat_without_flat_id():
    result = parse_feed(_feed(_flat(flat_id="")))
    assert result.lots == []
    assert result.skipped_count == 1


def test_skips_flat_with_unknown_status():
    result = parse_feed(_feed(_flat(status="UNKNOWN")))
    assert result.lots == []
    assert result.skipped_count == 1


def test_multiple_flats_share_object_level_project_and_address():
    result = parse_feed(_feed(_flat(flat_id="a"), _flat(flat_id="b")))
    assert len(result.lots) == 2
    assert all(lot.project_name == "ЖК Тест" for lot in result.lots)


def test_invalid_xml_raises_feed_parse_error():
    with pytest.raises(FeedParseError):
        parse_feed(b"not xml at all <<<")


def test_wrong_root_tag_raises_feed_parse_error():
    with pytest.raises(FeedParseError):
        parse_feed(b"<not_a_feed></not_a_feed>")


@pytest.mark.skipif(not FEED_ROOT.exists(), reason="Пример фида feeds/element.xml отсутствует")
def test_real_feed_smoke():
    with open(FEED_ROOT, "rb") as f:
        result = parse_feed(f)

    assert result.skipped_count == 0
    assert len(result.lots) > 1000
    assert all(lot.external_id for lot in result.lots)
