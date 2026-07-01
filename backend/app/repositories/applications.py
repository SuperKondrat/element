from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.enums import ApplicationStatus
from app.schemas.application import ApplicationCreate


def create(db: Session, data: ApplicationCreate) -> Application:
    application = Application(
        lot_id=data.lot_id,
        contact_name=data.contact_name,
        contact_phone=data.contact_phone,
        contact_email=data.contact_email,
        comment=data.comment,
        status=ApplicationStatus.NEW,
    )
    db.add(application)
    db.flush()
    return application


def list_all(db: Session) -> list[Application]:
    return list(db.execute(select(Application).order_by(Application.created_at.desc())).scalars().all())
