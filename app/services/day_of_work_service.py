from datetime import date, timedelta

from app.extensions import db
from app.models.day_of_work import DayOfWork
from app.services.prisoner_service import get_by_id as get_prisoner_by_id, get_by_cpf
from app.errors import ResourceNotFound, BusinessRuleViolation

DAYS_REDUCTION = 1


def _resolve_prisoner(identifier: str):
    if len(identifier) == 36:
        return get_prisoner_by_id(identifier)
    return get_by_cpf(identifier)


def _get_owned(prisoner, work_day_id: str) -> DayOfWork:
    work_day = db.session.scalar(
        db.select(DayOfWork).where(
            DayOfWork.id == work_day_id,
            DayOfWork.prisoner_id == prisoner.id,
        )
    )
    if not work_day:
        raise ResourceNotFound("Work day not found")
    return work_day


def _assert_date_is_free(prisoner, work_date, ignore_id: str | None = None) -> None:
    query = db.select(DayOfWork).where(
        DayOfWork.prisoner_id == prisoner.id,
        DayOfWork.date == work_date,
    )
    if ignore_id:
        query = query.where(DayOfWork.id != ignore_id)

    if db.session.scalar(query):
        raise BusinessRuleViolation(
            f"Prisoner already has a work day registered on {work_date}"
        )


def get_all() -> list[DayOfWork]:
    return list(db.session.scalars(db.select(DayOfWork)))


def get_by_id(work_day_id: str) -> DayOfWork:
    work_day = db.session.get(DayOfWork, work_day_id)
    if not work_day:
        raise ResourceNotFound("Work day not found")
    return work_day


def get_by_prisoner(identifier: str) -> list[DayOfWork]:
    prisoner = _resolve_prisoner(identifier)
    return list(
        db.session.scalars(
            db.select(DayOfWork).where(DayOfWork.prisoner_id == prisoner.id)
        )
    )


def create(identifier: str, data: dict) -> DayOfWork:
    prisoner = _resolve_prisoner(identifier)

    work_date = data.get("date") or date.today()
    _assert_date_is_free(prisoner, work_date)

    work_day = DayOfWork(
        description=data["description"],
        date=work_date,
        prisoner_id=prisoner.id,
    )
    prisoner.updated_release_date -= timedelta(days=DAYS_REDUCTION)

    db.session.add(work_day)
    db.session.commit()
    return work_day


def update(identifier: str, work_day_id: str, data: dict) -> DayOfWork:
    prisoner = _resolve_prisoner(identifier)
    work_day = _get_owned(prisoner, work_day_id)

    new_date = data.get("date")
    if new_date and new_date != work_day.date:
        _assert_date_is_free(prisoner, new_date, ignore_id=work_day.id)
        work_day.date = new_date

    new_description = data.get("description")
    if new_description:
        work_day.description = new_description

    db.session.commit()
    return work_day


def delete(identifier: str, work_day_id: str) -> None:
    prisoner = _resolve_prisoner(identifier)
    work_day = _get_owned(prisoner, work_day_id)

    prisoner.updated_release_date += timedelta(days=DAYS_REDUCTION)
    db.session.delete(work_day)
    db.session.commit()
