from datetime import date
from app.extensions import db
from app.models.prisoner import Prisoner
from app.errors import ResourceNotFound, BusinessRuleViolation

def build_query(filters: dict):
    query = db.select(Prisoner)

    name = filters.get("name")
    if name:
        query = query.where(Prisoner.name.ilike(f"%{name}%"))

    cpf = filters.get("cpf")
    if cpf:
        query = query.where(Prisoner.cpf == cpf)

    return query.order_by(Prisoner.name)


def get_all() -> list[Prisoner]:
    return list(db.session.scalars(db.select(Prisoner)))

def get_by_id(prisoner_id: str) -> Prisoner:
    prisoner = db.session.get(Prisoner, prisoner_id)
    if not prisoner:
        raise ResourceNotFound("Prisoner not found")
    return prisoner

def get_by_cpf(cpf: str) -> Prisoner:
    prisoner = db.session.scalar(db.select(Prisoner).where(Prisoner.cpf == cpf))
    if not prisoner:
        raise ResourceNotFound("Prisoner not found")
    return prisoner

def create(data: dict) -> Prisoner:
    if db.session.scalar(db.select(Prisoner).where(Prisoner.cpf == data['cpf'])):
        raise BusinessRuleViolation("Prisoner already exists")

    prisoner = Prisoner(**data)
    prisoner.books_counter = 0
    prisoner.current_year = date.today().year
    prisoner.updated_release_date = prisoner.original_release_date

    db.session.add(prisoner)
    db.session.commit()
    return prisoner

def update(identifier: str, data: dict) -> Prisoner:
    if len(identifier) == 36:
        prisoner = get_by_id(identifier)
    else:
        prisoner = get_by_cpf(identifier)

    new_cpf = data.get('cpf')
    if new_cpf and new_cpf != prisoner.cpf:
        existing = db.session.scalar(
            db.select(Prisoner).where(Prisoner.cpf == new_cpf)
        )
        if existing:
            raise BusinessRuleViolation("CPF already belongs to another prisoner")

    for key, value in data.items():
        setattr(prisoner, key, value)

    db.session.commit()
    return prisoner


def delete(identifier: str) -> None:
    if len(identifier) == 36:
        prisoner = get_by_id(identifier)
    else:
        prisoner = get_by_cpf(identifier)

    db.session.delete(prisoner)
    db.session.commit()