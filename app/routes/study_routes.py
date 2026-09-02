from flask import Blueprint, request, jsonify

from app.services import study_service
from app.schemas.study_schema import StudySchema


bp = Blueprint("studies", __name__)

study_schema = StudySchema()
studies_schema = StudySchema(many=True)


@bp.get("/")
def get_all():
    prisoner_id = request.args.get("prisoner_id")

    if prisoner_id:
        studies = study_service.get_by_prisoner_id(prisoner_id)
    else:
        studies = study_service.get_all()

    return jsonify(studies_schema.dump(studies)), 200


@bp.get("/<study_id>")
def get_one(study_id: str):
    study = study_service.get_by_id(study_id)

    return jsonify(
        study_schema.dump(study)
    ), 200


@bp.post("/")
def create():
    data = study_schema.load(request.json)

    study = study_service.create(data)

    return jsonify(
        study_schema.dump(study)
    ), 201


@bp.put("/<study_id>")
def update(study_id: str):
    data = study_schema.load(request.json)

    study = study_service.update(
        study_id,
        data
    )

    return jsonify(
        study_schema.dump(study)
    ), 200


@bp.patch("/<study_id>")
def patch(study_id: str):
    # Partial update
    data = study_schema.load(
        request.json,
        partial=True
    )

    study = study_service.update(
        study_id,
        data
    )

    return jsonify(
        study_schema.dump(study)
    ), 200


@bp.delete("/<study_id>")
def delete(study_id: str):
    study_service.delete(study_id)

    return "", 204