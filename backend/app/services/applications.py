from sqlalchemy.orm import Session

from app.models.application import Application
from app.repositories import applications as applications_repo
from app.repositories import lots as lots_repo
from app.schemas.application import ApplicationCreate
from app.services.exceptions import LotNotFoundError


def create_application(db: Session, data: ApplicationCreate) -> Application:
    if data.lot_id is not None and lots_repo.get_by_id(db, data.lot_id) is None:
        raise LotNotFoundError(data.lot_id)

    application = applications_repo.create(db, data)
    db.commit()
    db.refresh(application)
    return application


def list_applications(db: Session) -> list[Application]:
    return applications_repo.list_all(db)
