from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, SOP

sops_bp = Blueprint('sops', __name__)

@sops_bp.route('/', methods=['POST'])
@jwt_required()
def create_sop():
    data = request.json
    sop = SOP(title=data['title'], content=data['content'],
              department_id=data['department_id'], owner_id=get_jwt_identity())
    db.session.add(sop)
    db.session.commit()
    return jsonify({"msg": "SOP created"}), 201

@sops_bp.route('/', methods=['GET'])
@jwt_required()
def list_sops():
    user_id = get_jwt_identity()
    sops = SOP.query.filter_by(owner_id=user_id).all()
    return jsonify([{"id": s.id, "title": s.title} for s in sops])
