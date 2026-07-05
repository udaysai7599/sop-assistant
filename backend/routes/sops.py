from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import SOP, Department
from db import db

sops_bp = Blueprint('sops', __name__)


def get_or_create_department(department_id=None, department_name=None):
    if department_id:
        department = Department.query.get(department_id)
        if department:
            return department

    if department_name:
        department = Department.query.filter_by(name=department_name).first()
        if department:
            return department
        department = Department(name=department_name)
        db.session.add(department)
        db.session.flush()
        return department

    department = Department.query.filter_by(name='General').first()
    if not department:
        department = Department(name='General')
        db.session.add(department)
        db.session.flush()
    return department


@sops_bp.route('/', methods=['POST'])
@jwt_required()
def create_sop():
    data = request.json or {}
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    if not title or not content:
        return jsonify({"msg": "Title and content are required"}), 400

    department = get_or_create_department(
        department_id=data.get('department_id'),
        department_name=data.get('department_name')
    )
    sop = SOP(
        title=title,
        content=content,
        department_id=department.id,
        owner_id=int(get_jwt_identity())
    )
    db.session.add(sop)
    db.session.commit()
    return jsonify({"msg": "SOP created", "id": sop.id, "title": sop.title}), 201


@sops_bp.route('/', methods=['GET'])
@jwt_required()
def list_sops():
    user_id = int(get_jwt_identity())
    sops = SOP.query.filter_by(owner_id=user_id).all()
    payload = []
    for sop in sops:
        department = Department.query.get(sop.department_id)
        payload.append({
            "id": sop.id,
            "title": sop.title,
            "content": sop.content,
            "department_name": department.name if department else 'General'
        })
    return jsonify(payload)
