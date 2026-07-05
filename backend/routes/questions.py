from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import SOP, QnALog
from db import db
from rag import run_rag

questions_bp = Blueprint('questions', __name__)

@questions_bp.route('/', methods=['POST'])
@jwt_required()
def ask_question():
    data = request.json or {}
    sop_id = data.get('sop_id')
    question = (data.get('question') or '').strip()

    if not sop_id or not question:
        return jsonify({"msg": "SOP ID and question are required"}), 400

    sop = SOP.query.get(int(sop_id))
    if not sop:
        return jsonify({"msg": "SOP not found"}), 404

    answer, sources = run_rag(question, sop.content)

    log = QnALog(
        question=question,
        answer=answer,
        sources=sources,
        user_id=int(get_jwt_identity()),
        sop_id=sop.id
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"answer": answer, "sources": sources, "sop_title": sop.title})
