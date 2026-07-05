from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import SOP, QnALog, User
from db import db
from rag import run_rag

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
    question = (data.get('question') or '').strip()

    if not sop_id or not question:
        return jsonify({"msg": "SOP ID and question are required"}), 400

    sop = SOP.query.get(int(sop_id))
    if not sop:
        return jsonify({"msg": "SOP not found"}), 404

    # Generate answer using RAG on SOP content
    answer, sources = run_rag(question, sop.content)

    user_id = int(get_jwt_identity())
    log = QnALog(
        question=question,
        answer=answer,
        sources=sources,
        user_id=user_id,
        sop_id=sop.id
    )
    db.session.add(log)
    db.session.commit()

    owner = User.query.get(sop.owner_id)
    return jsonify({
        "answer": answer, 
        "sources": sources, 
        "sop_title": sop.title,
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
