from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import SOP, QnALog, User, Document, DocumentChunk
from db import db
from rag import run_rag
from services.document_service import build_document_chunks

questions_bp = Blueprint('questions', __name__)

@questions_bp.route('/', methods=['POST'])
@jwt_required()
def ask_question():
    """
    Ask a question about an SOP.
    Any authenticated user can ask questions about any SOP.
    The answer is generated using RAG on the SOP content.
    """
    data = request.json or {}
    sop_id = data.get('sop_id')
    document_id = data.get('document_id')
    question = (data.get('question') or '').strip()

    if not question:
        return jsonify({"msg": "A question is required"}), 400

    sop = None
    document = None
    context_source = None

    if sop_id:
        sop = SOP.query.get(int(sop_id))
        if not sop:
            return jsonify({"msg": "SOP not found"}), 404
        answer, sources = run_rag(question, sop.content)
        context_source = sop.title
    elif document_id:
        document = db.session.get(Document, int(document_id))
        if not document:
            return jsonify({"msg": "Document not found"}), 404
        chunks = [chunk.content for chunk in document.chunks]
        if not chunks:
            chunks = build_document_chunks(document.content)
        best_chunk = max(chunks, key=lambda chunk: len(set(question.lower().split()) & set(chunk.lower().split())), default="")
        answer, sources = run_rag(question, best_chunk or document.content)
        context_source = document.title
    else:
        return jsonify({"msg": "SOP ID or document ID is required"}), 400

    user_id = int(get_jwt_identity())
    log = QnALog(
        question=question,
        answer=answer,
        sources=sources,
        user_id=user_id,
        sop_id=sop.id if sop else None,
        document_id=document.id if document else None
    )
    db.session.add(log)
    db.session.commit()

    owner = User.query.get(sop.owner_id) if sop else None
    return jsonify({
        "answer": answer,
        "sources": sources,
        "sop_title": context_source,
        "sop_owner": owner.email if owner else 'Unknown'
    }), 200


@questions_bp.route('/history', methods=['GET'])
@jwt_required()
def get_question_history():
    """
    Get all Q&A history for the current user.
    """
    user_id = int(get_jwt_identity())
    logs = QnALog.query.filter_by(user_id=user_id).order_by(QnALog.id.desc()).all()
    
    payload = []
    for log in logs:
        sop = SOP.query.get(log.sop_id) if log.sop_id else None
        payload.append({
            'id': log.id,
            'question': log.question,
            'answer': log.answer,
            'sources': log.sources,
            'sop_title': sop.title if sop else 'Unknown SOP',
            'created_at': log.created_at.isoformat() if log.created_at else None
        })
    
    return jsonify(payload), 200


@questions_bp.route('/<int:question_id>', methods=['GET'])
@jwt_required()
def get_question(question_id):
    """
    Get a specific question by ID.
    Only the user who asked the question can view it.
    """
    user_id = int(get_jwt_identity())
    log = QnALog.query.get(question_id)
    
    if not log:
        return jsonify({"msg": "Question not found"}), 404
    
    if log.user_id != user_id:
        return jsonify({"msg": "You can only view your own questions"}), 403
    
    sop = SOP.query.get(log.sop_id) if log.sop_id else None
    
    return jsonify({
        'id': log.id,
        'question': log.question,
        'answer': log.answer,
        'sources': log.sources,
        'sop_title': sop.title if sop else 'Unknown SOP',
        'created_at': log.created_at.isoformat() if log.created_at else None
    }), 200
