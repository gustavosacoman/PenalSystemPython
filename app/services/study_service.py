from datetime import date, timedelta

from app.extensions import db
from app.models.study import Study
from app.services.prisoner_service import get_by_id
from app.errors import ResourceNotFound, BusinessRuleViolation


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


def build_query_for_prisoner(prisoner_id: str, filters: dict):
    prisoner = get_by_id_from_prisoner(prisoner_id)
    return build_query(filters, prisoner_id=prisoner.id)


def get_all() -> list[Study]:
    return list(
        db.session.scalars(
            db.select(Study)
        )
    )


def get_by_id(study_id: str) -> Study:
    study = db.session.get(Study, study_id)

    if not study:
        raise ResourceNotFound("Study not found")

    return study


def get_by_prisoner_id(prisoner_id: str) -> list[Study]:
    # Garante que o preso existe
    get_by_id_prisoner = get_by_id_prisoner_service(prisoner_id)

    return list(
        db.session.scalars(
            db.select(Study)
            .where(Study.prisoner_id == get_by_id_prisoner.id)
        )
    )


def get_by_id_prisoner_service(prisoner_id: str):
    return get_by_id_from_prisoner(prisoner_id)


def get_by_id_from_prisoner(prisoner_id: str):
    from app.services.prisoner_service import get_by_id as get_prisoner_by_id

    return get_prisoner_by_id(prisoner_id)


def create(data: dict) -> Study:
    prisoner = get_by_id_from_prisoner(data["prisoner_id"])

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


def update(study_id: str, data: dict) -> Study:
    study = get_by_id(study_id)

    # O preso não é alterado em uma atualização.
    # Isso evita transferir uma remição já aplicada
    # de um preso para outro.
    if "subject" in data:
        study.subject = data["subject"]

    if "date" in data:
        _assert_date_is_free(study.prisoner_id, data["date"], ignore_id=study.id)
        study.date = data["date"]

    db.session.commit()

    return study


def delete(study_id: str) -> None:
    study = get_by_id(study_id)

    prisoner = get_by_id_from_prisoner(study.prisoner_id)

    # Ao remover o estudo, devolvemos o dia de pena
    # que havia sido remido.
    prisoner.updated_release_date += timedelta(days=1)

    db.session.delete(study)
    db.session.commit()
