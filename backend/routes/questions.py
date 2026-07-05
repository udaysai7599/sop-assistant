from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, SOP, QnALog
from rag import run_rag

questions_bp = Blueprint('questions', __name__)

@questions_bp.route('/', methods=['POST'])
@jwt_required()
def ask_question():
    data = request.json
    sop_id = data['sop_id']
    question = data['question']
    sop = SOP.query.get(sop_id)
    answer, sources = run_rag(question, sop.content)

    log = QnALog(question=question, answer=answer, sources=sources,
                 user_id=get_jwt_identity(), sop_id=sop_id)
    db.session.add(log)
    db.session.commit()

    return jsonify({"answer": answer, "sources": sources})
