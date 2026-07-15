from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Document, DocumentChunk, User
from db import db
from services.document_service import extract_text_from_upload, build_document_chunks


documents_bp = Blueprint('documents', __name__)


@documents_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload a text-based document and index it for later retrieval."""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user or not user.is_admin():
        return jsonify({"msg": "Only admins can upload documents"}), 403

    title = request.form.get('title', '').strip() or 'Untitled Document'
    uploaded_file = request.files.get('file')
    if not uploaded_file or not uploaded_file.filename:
        return jsonify({"msg": "A file is required"}), 400

    text_content = extract_text_from_upload(uploaded_file)
    if not text_content.strip():
        return jsonify({"msg": "No readable text could be extracted from the file"}), 400

    document = Document(title=title, content=text_content, owner_id=user_id)
    db.session.add(document)
    db.session.flush()

    chunks = build_document_chunks(text_content)
    for chunk_index, chunk_text in enumerate(chunks):
        db.session.add(DocumentChunk(document_id=document.id, chunk_index=chunk_index, content=chunk_text))

    db.session.commit()

    return jsonify({
        "msg": "Document uploaded successfully",
        "id": document.id,
        "title": document.title,
        "chunk_count": len(chunks)
    }), 201


@documents_bp.route('/', methods=['GET'])
@jwt_required()
def list_documents():
    """List documents visible to the current user."""
    documents = Document.query.order_by(Document.id.desc()).all()
    payload = [{
        "id": doc.id,
        "title": doc.title,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
        "chunk_count": len(doc.chunks)
    } for doc in documents]
    return jsonify(payload), 200
