from datetime import timedelta

from app.extensions import db
from app.models.day_of_work import DayOfWork
from app.services.prisoner_service import get_by_id, get_by_cpf
from app.errors import ResourceNotFound


def create(identifier: str, data: dict) -> DayOfWork:
    if len(identifier) == 36:
        prisoner = get_by_id(identifier)
    else:
        prisoner = get_by_cpf(identifier)

    work_day = DayOfWork(
        description=data["description"],
        date=data.get("date"),
        prisoner_id=prisoner.id,
    )
    prisoner.updated_release_date -= timedelta(days=1)

    db.session.add(work_day)
    db.session.commit()
    return work_day


def delete(identifier: str, work_day_id: str) -> None:
    if len(identifier) == 36:
        prisoner = get_by_id(identifier)
    else:
        prisoner = get_by_cpf(identifier)

    work_day = db.session.scalar(
        db.select(DayOfWork).where(
            DayOfWork.id == work_day_id,
            DayOfWork.prisoner_id == prisoner.id,
        )
    )
    if not work_day:
        raise ResourceNotFound("Work day not found")

    prisoner.updated_release_date += timedelta(days=1)
    db.session.delete(work_day)
    db.session.commit()
