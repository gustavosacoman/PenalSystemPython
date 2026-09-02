from flask import Blueprint, request, jsonify
from app.services import prisoner_service
from app.schemas.prisoner_schema import PrisonerSchema, UpdatePrisonerSchema
from app.schemas.day_of_work_schema import DayOfWorkSchema
from app.services import day_of_work_service

bp = Blueprint("prisoners", __name__)

prisoner_schema = PrisonerSchema()
prisoners_schema = PrisonerSchema(many=True)
update_schema = UpdatePrisonerSchema(partial=True)
day_of_work_schema = DayOfWorkSchema()
day_of_works_schema = DayOfWorkSchema(many=True)


@bp.get("/")
def get_all():
    prisoners = prisoner_service.get_all()
    return jsonify(prisoners_schema.dump(prisoners)), 200

@bp.get("/<identifier>")
def get_one(identifier: str):
    if len(identifier) == 36:
        prisoner = prisoner_service.get_by_id(identifier)
    else:
        prisoner = prisoner_service.get_by_cpf(identifier)
    return jsonify(prisoner_schema.dump(prisoner)), 200

@bp.post("/")
def create():
    data = prisoner_schema.load(request.json)
    prisoner = prisoner_service.create(data)
    return jsonify({"message": "Registered Successful!", "data": prisoner_schema.dump(prisoner)}), 201

@bp.put("/<identifier>")
def update(identifier: str):
    data = update_schema.load(request.json)
    prisoner = prisoner_service.update(identifier, data)
    return jsonify({"message": "Prisoner updated successful!", "data": prisoner_schema.dump(prisoner)}), 200

@bp.delete("/<identifier>")
def delete(identifier: str):
    prisoner_service.delete(identifier)
    return jsonify({"message": "Prisoner deleted successful"}), 200


@bp.post("/<identifier>/days-of-work")
def create_day_of_work(identifier: str):
    data = day_of_work_schema.load(request.json)
    work_day = day_of_work_service.create(identifier, data)
    return jsonify(day_of_work_schema.dump(work_day)), 201


@bp.get("/<identifier>/days-of-work")
def get_days_of_work(identifier: str):
    work_days = day_of_work_service.get_all(identifier)
    return jsonify(day_of_works_schema.dump(work_days)), 200


@bp.delete("/<identifier>/days-of-work/<work_day_id>")
def delete_day_of_work(identifier: str, work_day_id: str):
    day_of_work_service.delete(identifier, work_day_id)
    return jsonify({"message": "Work day deleted successful"}), 200

