from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import QnALog, SOP

answers_bp = Blueprint('answers', __name__)


@answers_bp.route('/', methods=['GET'])
@jwt_required()
def list_answers():
    """
    Get all Q&A history for the current user.
    Answers are sorted by most recent first.
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
            'sop_id': log.sop_id,
            'created_at': log.created_at.isoformat() if log.created_at else None
        })
    
    return jsonify(payload), 200


@answers_bp.route('/<int:answer_id>', methods=['GET'])
@jwt_required()
def get_answer(answer_id):
    """
    Get a specific answer by ID.
    Only the user who asked the question can view it.
    """
    user_id = int(get_jwt_identity())
    log = QnALog.query.get(answer_id)
    
    if not log:
        return jsonify({"msg": "Answer not found"}), 404
    
    if log.user_id != user_id:
        return jsonify({"msg": "You can only view your own answers"}), 403
    
    sop = SOP.query.get(log.sop_id) if log.sop_id else None
    
    return jsonify({
        'id': log.id,
        'question': log.question,
        'answer': log.answer,
        'sources': log.sources,
        'sop_title': sop.title if sop else 'Unknown SOP',
        'created_at': log.created_at.isoformat() if log.created_at else None
    }), 200
