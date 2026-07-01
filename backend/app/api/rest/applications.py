from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin
from app.db import get_db
from app.schemas.application import ApplicationCreate, ApplicationRead
from app.services import applications as applications_service

router = APIRouter(tags=["applications"])


@router.post("/applications", response_model=ApplicationRead, status_code=201)
def create_application(data: ApplicationCreate, db: Session = Depends(get_db)) -> ApplicationRead:
    application = applications_service.create_application(db, data)
    return ApplicationRead.model_validate(application)


@router.get("/admin/applications", response_model=list[ApplicationRead])
def list_applications(
    db: Session = Depends(get_db), admin: str = Depends(get_current_admin)
) -> list[ApplicationRead]:
    return [ApplicationRead.model_validate(a) for a in applications_service.list_applications(db)]
