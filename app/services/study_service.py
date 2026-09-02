from datetime import timedelta

from app.extensions import db
from app.models.study import Study
from app.services.prisoner_service import get_by_id
from app.errors import ResourceNotFound


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

    study = Study(
        prisoner_id=prisoner.id,
        subject=data["subject"],
        date=data.get("date")
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
