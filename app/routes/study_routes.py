from flask import Blueprint, request, jsonify

from app.services import study_service
from app.schemas.study_schema import StudySchema, UpdateStudySchema
from app.pagination import paginate

bp = Blueprint("studies", __name__)

study_schema = StudySchema()
studies_schema = StudySchema(many=True)
patch_schema = UpdateStudySchema(partial=True)


@bp.get("/studies/")
def get_all():
    prisoner_id = request.args.get("prisoner_id")

    if prisoner_id:
        query = study_service.build_query_for_prisoner(prisoner_id, request.args)
    else:
        query = study_service.build_query(request.args)

    return jsonify(paginate(query, studies_schema)), 200


@bp.get("/studies/<study_id>")
def get_one(study_id: str):
    study = study_service.get_by_id(study_id)
    return jsonify(study_schema.dump(study)), 200


@bp.get("/prisoners/<identifier>/studies")
def get_by_prisoner(identifier: str):
    query = study_service.build_query_for_prisoner(identifier, request.args)
    return jsonify(paginate(query, studies_schema)), 200


@bp.post("/prisoners/<identifier>/studies")
def create(identifier: str):
    data = study_schema.load(request.json)
    study = study_service.create(identifier, data)
    return jsonify({"message": "Study registered successful!", "data": study_schema.dump(study)}), 201


@bp.put("/prisoners/<identifier>/studies/<study_id>")
def update(identifier: str, study_id: str):
    data = study_schema.load(request.json)
    study = study_service.update(identifier, study_id, data)
    return jsonify({"message": "Study updated successful!", "data": study_schema.dump(study)}), 200


@bp.patch("/prisoners/<identifier>/studies/<study_id>")
def patch(identifier: str, study_id: str):
    data = patch_schema.load(request.json)
    study = study_service.update(identifier, study_id, data)
    return jsonify({"message": "Study updated successful!", "data": study_schema.dump(study)}), 200


@bp.delete("/prisoners/<identifier>/studies/<study_id>")
def delete(identifier: str, study_id: str):
    study_service.delete(identifier, study_id)
    return "", 204
