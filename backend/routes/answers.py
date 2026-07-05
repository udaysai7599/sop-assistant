from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import QnALog, SOP

answers_bp = Blueprint('answers', __name__)


@answers_bp.route('/', methods=['GET'])
@jwt_required()
def list_answers():
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
            'sop_title': sop.title if sop else 'Unknown SOP'
        })
    return jsonify(payload)
