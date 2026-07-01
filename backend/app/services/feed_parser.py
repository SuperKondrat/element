import logging
from dataclasses import dataclass
from typing import BinaryIO

from defusedxml import ElementTree as ET

from app.models.enums import LotStatus

logger = logging.getLogger(__name__)

# Статусы в фиде (см. п.8.3 PLAN.md — проверено на реальном element.xml,
# других значений не встречается).
_STATUS_MAP: dict[str, LotStatus] = {
    "FREE": LotStatus.FOR_SALE,
    "RESERVED": LotStatus.RESERVED,
    "SOLD": LotStatus.SOLD,
}


class FeedParseError(Exception):
    """Фид не является валидным XML или не содержит ожидаемой структуры."""


@dataclass(frozen=True, slots=True)
class ParsedLot:
    external_id: str
    project_name: str
    address: str
    rooms: int
    area: float
    floor: int
    price: float
    price_base: float
    status: LotStatus


@dataclass(frozen=True, slots=True)
class ParseResult:
    lots: list[ParsedLot]
    skipped_count: int


def _text(el, tag: str, default: str = "") -> str:
    value = el.findtext(tag)
    return value.strip() if value else default


def _to_int(value: str, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _to_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_feed(source: BinaryIO | bytes) -> ParseResult:
    """Парсит XML-фид (feed > object > buildings > building > flats > flat)
    в плоский список лотов. Поля, не входящие в модель лота, отбрасываются
    (см. п.8.3 PLAN.md)."""
    try:
        root = ET.fromstring(source) if isinstance(source, bytes) else ET.parse(source).getroot()
    except ET.ParseError as exc:
        raise FeedParseError(f"Некорректный XML: {exc}") from exc

    if root.tag != "feed":
        raise FeedParseError(f"Ожидался корневой элемент <feed>, получен <{root.tag}>")

    lots: list[ParsedLot] = []
    skipped = 0

    for obj in root.findall("object"):
        project_name = _text(obj, "name")
        address = _text(obj, "address")

        for flat in obj.findall("buildings/building/flats/flat"):
            external_id = _text(flat, "flat_id")
            status_raw = _text(flat, "status").upper()
            status = _STATUS_MAP.get(status_raw)

            if not external_id or status is None:
                logger.warning(
                    "feed_parser: пропущен лот — flat_id=%r status=%r", external_id, status_raw
                )
                skipped += 1
                continue

            lots.append(
                ParsedLot(
                    external_id=external_id,
                    project_name=project_name,
                    address=address,
                    rooms=_to_int(_text(flat, "room")),
                    area=_to_float(_text(flat, "area")),
                    floor=_to_int(_text(flat, "floor")),
                    price=_to_float(_text(flat, "price")),
                    price_base=_to_float(_text(flat, "price_base")),
                    status=status,
                )
            )

    return ParseResult(lots=lots, skipped_count=skipped)
