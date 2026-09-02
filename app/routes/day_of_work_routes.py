from flask import Blueprint, request, jsonify
from app.services import day_of_work_service
from app.schemas.day_of_work_schema import DayOfWorkSchema, UpdateDayOfWorkSchema
from app.pagination import paginate

bp = Blueprint("days_of_work", __name__)

day_of_work_schema = DayOfWorkSchema()
days_of_work_schema = DayOfWorkSchema(many=True)
patch_schema = UpdateDayOfWorkSchema(partial=True)

@bp.get("/days-of-work/")
def get_all():
    query = day_of_work_service.build_query(request.args)
    return jsonify(paginate(query, days_of_work_schema)), 200

@bp.get("/days-of-work/<work_day_id>")
def get_one(work_day_id: str):
    work_day = day_of_work_service.get_by_id(work_day_id)
    return jsonify(day_of_work_schema.dump(work_day)), 200

@bp.get("/prisoners/<identifier>/days-of-work")
def get_by_prisoner(identifier: str):
    query = day_of_work_service.build_query_for_prisoner(identifier, request.args)
    return jsonify(paginate(query, days_of_work_schema)), 200

@bp.post("/prisoners/<identifier>/days-of-work")
def create(identifier: str):
    data = day_of_work_schema.load(request.json)
    work_day = day_of_work_service.create(identifier, data)
    return jsonify({"message": "Work day registered successful!", "data": day_of_work_schema.dump(work_day)}), 201

@bp.put("/prisoners/<identifier>/days-of-work/<work_day_id>")
def update(identifier: str, work_day_id: str):
    data = day_of_work_schema.load(request.json)
    work_day = day_of_work_service.update(identifier, work_day_id, data)
    return jsonify({"message": "Work day updated successful!", "data": day_of_work_schema.dump(work_day)}), 200

@bp.delete("/prisoners/<identifier>/days-of-work/<work_day_id>")
def delete(identifier: str, work_day_id: str):
    day_of_work_service.delete(identifier, work_day_id)
    return "", 204


@bp.patch("/prisoners/<identifier>/days-of-work/<work_day_id>")
def patch(identifier: str, work_day_id: str):
    data = patch_schema.load(request.json)
    work_day = day_of_work_service.update(identifier, work_day_id, data)
    return jsonify({"message": "Work day updated successful!", "data": day_of_work_schema.dump(work_day)}), 200
