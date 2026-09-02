from datetime import date, timedelta

from app.extensions import db
from app.models.study import Study
from app.services.prisoner_service import get_by_id as get_prisoner_by_id, get_by_cpf
from app.errors import ResourceNotFound, BusinessRuleViolation


def _resolve_prisoner(identifier: str):
    if len(identifier) == 36:
        return get_prisoner_by_id(identifier)
    return get_by_cpf(identifier)


def _get_owned(prisoner, study_id: str) -> Study:
    study = db.session.scalar(
        db.select(Study).where(
            Study.id == study_id,
            Study.prisoner_id == prisoner.id,
        )
    )
    if not study:
        raise ResourceNotFound("Study not found")
    return study


def _assert_date_is_free(prisoner_id: str, study_date, ignore_id: str | None = None) -> None:
    query = db.select(Study).where(
        Study.prisoner_id == prisoner_id,
        Study.date == study_date,
    )
    if ignore_id:
        query = query.where(Study.id != ignore_id)

    if db.session.scalar(query):
        raise BusinessRuleViolation(
            f"Prisoner already has a study registered on {study_date}"
        )


def build_query(filters: dict, prisoner_id: str | None = None):
    query = db.select(Study)

    if prisoner_id:
        query = query.where(Study.prisoner_id == prisoner_id)

    subject = filters.get("subject")
    if subject:
        query = query.where(Study.subject.ilike(f"%{subject}%"))

    date_from = filters.get("date_from")
    if date_from:
        query = query.where(Study.date >= date_from)

    date_to = filters.get("date_to")
    if date_to:
        query = query.where(Study.date <= date_to)

    return query.order_by(Study.date.desc())


def build_query_for_prisoner(identifier: str, filters: dict):
    prisoner = _resolve_prisoner(identifier)
    return build_query(filters, prisoner_id=prisoner.id)


def get_all() -> list[Study]:
    return list(db.session.scalars(db.select(Study)))


def get_by_id(study_id: str) -> Study:
    study = db.session.get(Study, study_id)

    if not study:
        raise ResourceNotFound("Study not found")

    return study


def get_by_prisoner(identifier: str) -> list[Study]:
    prisoner = _resolve_prisoner(identifier)
    return list(
        db.session.scalars(db.select(Study).where(Study.prisoner_id == prisoner.id))
    )


def create(identifier: str, data: dict) -> Study:
    prisoner = _resolve_prisoner(identifier)

    study_date = data.get("date") or date.today()
    _assert_date_is_free(prisoner.id, study_date)

    study = Study(
        prisoner_id=prisoner.id,
        subject=data["subject"],
        date=study_date
    )

    # Cada dia de estudo reduz 1 dia da pena.
    prisoner.updated_release_date -= timedelta(days=1)

    db.session.add(study)
    db.session.commit()

    return study


def update(identifier: str, study_id: str, data: dict) -> Study:
    prisoner = _resolve_prisoner(identifier)
    study = _get_owned(prisoner, study_id)

    # O preso vem da rota e prisoner_id nao e carregado do payload:
    # isso evita transferir uma remicao ja aplicada de um preso
    # para outro.
    if "subject" in data:
        study.subject = data["subject"]

    if "date" in data:
        _assert_date_is_free(prisoner.id, data["date"], ignore_id=study.id)
        study.date = data["date"]

    db.session.commit()

    return study


def delete(identifier: str, study_id: str) -> None:
    prisoner = _resolve_prisoner(identifier)
    study = _get_owned(prisoner, study_id)

    # Ao remover o estudo, devolvemos o dia de pena
    # que havia sido remido.
    prisoner.updated_release_date += timedelta(days=1)

    db.session.delete(study)
    db.session.commit()
