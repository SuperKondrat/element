from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin
from app.db import get_db
from app.schemas.booking import BookingCreate, BookingRead
from app.services import bookings as bookings_service

router = APIRouter(tags=["bookings"])


@router.post("/bookings", response_model=BookingRead, status_code=201)
def create_booking(data: BookingCreate, db: Session = Depends(get_db)) -> BookingRead:
    booking = bookings_service.create_booking(db, data)
    return BookingRead.model_validate(booking)


@router.get("/admin/bookings", response_model=list[BookingRead])
def list_bookings(
    db: Session = Depends(get_db), admin: str = Depends(get_current_admin)
) -> list[BookingRead]:
    return [BookingRead.model_validate(b) for b in bookings_service.list_bookings(db)]
