import os
import time
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import SOP, Department, User, SOPDocument
from db import db

sops_bp = Blueprint('sops', __name__)

ALLOWED_DOCUMENT_EXTENSIONS = {'.txt', '.md', '.csv', '.pdf', '.doc', '.docx'}


def _ensure_upload_dir():
    base_dir = Path(__file__).resolve().parents[1]
    upload_dir = base_dir / 'uploads' / 'documents'
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def _extract_text_for_rag(file_bytes, suffix):
    if suffix in {'.txt', '.md', '.csv'}:
        return file_bytes.decode('utf-8', errors='ignore')
    return ''


def _document_payload(document):
    return {
        'id': document.id,
        'title': document.title,
        'original_filename': document.original_filename,
        'download_url': f"/sops/documents/{document.id}/download",
        'created_at': document.created_at.isoformat() if document.created_at else None
    }


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
        department = Department.query.get(sop.department_id)
        owner = User.query.get(sop.owner_id)
        
        payload.append({
            "id": sop.id,
            "title": sop.title,
            "content": sop.content,
            "department_name": department.name if department else 'General',
            "owner_email": owner.email if owner else 'Unknown',
            "owner_id": sop.owner_id,
            "is_owner": sop.owner_id == user_id,
            "documents": [_document_payload(doc) for doc in sop.documents]
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
        "owner_email": owner.email if owner else 'Unknown',
        "documents": [_document_payload(doc) for doc in sop.documents]
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


@sops_bp.route('/<int:sop_id>/documents', methods=['POST'])
@jwt_required()
def upload_document(sop_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    sop = SOP.query.get(sop_id)

    if not sop:
        return jsonify({"msg": "SOP not found"}), 404

    if not user or not user.is_admin() or sop.owner_id != user_id:
        return jsonify({"msg": "Only the admin who created this SOP can upload documents"}), 403

    if 'document_file' not in request.files:
        return jsonify({"msg": "document_file is required"}), 400

    uploaded = request.files['document_file']
    if not uploaded or not uploaded.filename:
        return jsonify({"msg": "A valid file is required"}), 400

    original_filename = uploaded.filename
    safe_name = secure_filename(original_filename)
    suffix = Path(safe_name).suffix.lower()
    if suffix not in ALLOWED_DOCUMENT_EXTENSIONS:
        return jsonify({"msg": "Unsupported document format"}), 400

    file_bytes = uploaded.read()
    if not file_bytes:
        return jsonify({"msg": "Uploaded file is empty"}), 400

    upload_dir = _ensure_upload_dir()
    unique_name = f"sop{sop_id}_user{user_id}_{int(time.time())}_{safe_name}"
    destination = upload_dir / unique_name
    with open(destination, 'wb') as f:
        f.write(file_bytes)

    extracted_text = _extract_text_for_rag(file_bytes, suffix)
    title = (request.form.get('document_title') or Path(original_filename).stem).strip() or Path(original_filename).stem

    document = SOPDocument(
        title=title,
        original_filename=original_filename,
        file_path=str(destination),
        extracted_text=extracted_text,
        uploaded_by=user_id,
        sop_id=sop_id
    )
    db.session.add(document)
    db.session.commit()

    return jsonify({
        'msg': 'Document uploaded',
        'document': _document_payload(document)
    }), 201


@sops_bp.route('/<int:sop_id>/documents', methods=['GET'])
@jwt_required()
def list_sop_documents(sop_id):
    sop = SOP.query.get(sop_id)
    if not sop:
        return jsonify({"msg": "SOP not found"}), 404

    return jsonify([_document_payload(doc) for doc in sop.documents]), 200


@sops_bp.route('/documents/<int:document_id>/download', methods=['GET'])
@jwt_required()
def download_document(document_id):
    document = SOPDocument.query.get(document_id)
    if not document:
        return jsonify({"msg": "Document not found"}), 404

    path = document.file_path
    if not path or not os.path.exists(path):
        return jsonify({"msg": "Document file missing on server"}), 404

    return send_file(path, as_attachment=True, download_name=document.original_filename)
