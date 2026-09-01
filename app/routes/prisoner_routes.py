from flask import Blueprint, request, jsonify
from app.services import prisoner_service
from app.schemas.prisoner_schema import PrisonerSchema, UpdatePrisonerSchema

bp = Blueprint("prisoners", __name__)

prisoner_schema = PrisonerSchema()
prisoners_schema = PrisonerSchema(many=True)
update_schema = UpdatePrisonerSchema()

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

