from fastapi import APIRouter

from app.api.rest.applications import router as applications_router
from app.api.rest.auth import router as auth_router
from app.api.rest.bookings import router as bookings_router
from app.api.rest.lot_sets import router as lot_sets_router
from app.api.rest.lots import router as lots_router

router = APIRouter(prefix="/api")
router.include_router(auth_router)
router.include_router(lots_router)
router.include_router(bookings_router)
router.include_router(applications_router)
router.include_router(lot_sets_router)
