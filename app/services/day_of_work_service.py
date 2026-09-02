from datetime import timedelta

from app.extensions import db
from app.models.day_of_work import DayOfWork
from app.services.prisoner_service import get_by_id, get_by_cpf
from app.errors import ResourceNotFound


def build_query_for_prisoner(identifier: str, filters: dict):
    if len(identifier) == 36:
        prisoner = get_by_id(identifier)
    else:
        prisoner = get_by_cpf(identifier)

    query = db.select(DayOfWork).where(DayOfWork.prisoner_id == prisoner.id)

    description = filters.get("description")
    if description:
        query = query.where(DayOfWork.description.ilike(f"%{description}%"))

    date_from = filters.get("date_from")
    if date_from:
        query = query.where(DayOfWork.date >= date_from)

    date_to = filters.get("date_to")
    if date_to:
        query = query.where(DayOfWork.date <= date_to)

    return query.order_by(DayOfWork.date.desc())


def get_all(identifier: str) -> list[DayOfWork]:
    if len(identifier) == 36:
        prisoner = get_by_id(identifier)
    else:
        prisoner = get_by_cpf(identifier)

    return list(
        db.session.scalars(
            db.select(DayOfWork).where(DayOfWork.prisoner_id == prisoner.id)
        )
    )


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
