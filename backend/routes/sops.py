from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import SOP, Department, User
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
    """
    Create a new SOP. Only admins can create SOPs.
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user or not user.is_admin():
        return jsonify({"msg": "Only admins can create SOPs"}), 403

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
        owner_id=user_id
    )
    db.session.add(sop)
    db.session.commit()
    return jsonify({
        "msg": "SOP created", 
        "id": sop.id, 
        "title": sop.title
    }), 201


@sops_bp.route('/', methods=['GET'])
@jwt_required()
def list_all_sops():
    """
    List all available SOPs.
    - Admins can see all SOPs they created
    - Regular users can see all SOPs for asking questions
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    # Get all SOPs
    sops = SOP.query.all()
    payload = []
    
    for sop in sops:
        department = db.session.get(Department, sop.department_id)
        owner = db.session.get(User, sop.owner_id)
        
        payload.append({
            "id": sop.id,
            "title": sop.title,
            "content": sop.content,
            "department_name": department.name if department else 'General',
            "owner_email": owner.email if owner else 'Unknown',
            "owner_id": sop.owner_id,
            "is_owner": sop.owner_id == user_id
        })
    
    return jsonify(payload), 200


@sops_bp.route('/my-sops', methods=['GET'])
@jwt_required()
def list_my_sops():
    """
    List only SOPs created by the current user (admin only).
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user or not user.is_admin():
        return jsonify({"msg": "Only admins can view their SOPs"}), 403
    
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
    
    return jsonify(payload), 200


@sops_bp.route('/<int:sop_id>', methods=['GET'])
@jwt_required()
def get_sop(sop_id):
    """
    Get a specific SOP by ID.
    Any authenticated user can view any SOP.
    """
    sop = SOP.query.get(sop_id)
    if not sop:
        return jsonify({"msg": "SOP not found"}), 404
    
    department = Department.query.get(sop.department_id)
    owner = User.query.get(sop.owner_id)
    
    return jsonify({
        "id": sop.id,
        "title": sop.title,
        "content": sop.content,
        "department_name": department.name if department else 'General',
        "owner_email": owner.email if owner else 'Unknown'
    }), 200


@sops_bp.route('/<int:sop_id>', methods=['PUT'])
@jwt_required()
def update_sop(sop_id):
    """
    Update a SOP. Only the admin who created it can update it.
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    sop = SOP.query.get(sop_id)
    if not sop:
        return jsonify({"msg": "SOP not found"}), 404
    
    if not user or not user.is_admin() or sop.owner_id != user_id:
        return jsonify({"msg": "Only the admin who created this SOP can update it"}), 403
    
    data = request.json or {}
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    department_name = data.get('department_name', '').strip()
    
    if not title and not content and not department_name:
        return jsonify({"msg": "At least one field (title, content, or department_name) is required"}), 400
    
    if title:
        sop.title = title
    if content:
        sop.content = content
    if department_name:
        department = get_or_create_department(department_name=department_name)
        sop.department_id = department.id
    
    db.session.commit()
    
    return jsonify({
        "msg": "SOP updated",
        "id": sop.id,
        "title": sop.title,
        "content": sop.content,
        "department_name": Department.query.get(sop.department_id).name if sop.department_id else 'General'
    }), 200


@sops_bp.route('/<int:sop_id>', methods=['DELETE'])
@jwt_required()
def delete_sop(sop_id):
    """
    Delete a SOP. Only the admin who created it can delete it.
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    sop = SOP.query.get(sop_id)
    if not sop:
        return jsonify({"msg": "SOP not found"}), 404
    
    if not user or not user.is_admin() or sop.owner_id != user_id:
        return jsonify({"msg": "Only the admin who created this SOP can delete it"}), 403
    
    db.session.delete(sop)
    db.session.commit()
    
    return jsonify({"msg": "SOP deleted"}), 200
