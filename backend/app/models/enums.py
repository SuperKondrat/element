import enum


class LotStatus(str, enum.Enum):
    FOR_SALE = "for_sale"
    RESERVED = "reserved"
    SOLD = "sold"


class BookingStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class ApplicationStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
