from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import SOP, QnALog, User, Department
from db import db
from rag import run_rag
import json

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
    department_name = (data.get('department_name') or '').strip()

    if not question:
        return jsonify({"msg": "Question is required"}), 400

    selected_sop = None
    sop_candidates = []
    if sop_id is not None:
        selected_sop = SOP.query.get(int(sop_id))
        if not selected_sop:
            return jsonify({"msg": "SOP not found"}), 404
        if department_name:
            selected_department = Department.query.get(selected_sop.department_id) if selected_sop.department_id else None
            if not selected_department or selected_department.name.lower() != department_name.lower():
                return jsonify({"msg": "Selected SOP does not belong to that department"}), 400
        sop_candidates = [selected_sop]
    else:
        if department_name:
            sop_candidates = (
                SOP.query.join(Department, SOP.department_id == Department.id)
                .filter(db.func.lower(Department.name) == department_name.lower())
                .all()
            )
            if not sop_candidates:
                return jsonify({"msg": "No SOPs found for that department"}), 404
        else:
            sop_candidates = SOP.query.all()
        if not sop_candidates:
            return jsonify({"msg": "No SOPs available yet"}), 404

    retrieval_input = []
    for sop in sop_candidates:
        retrieval_input.append({
            'sop_id': sop.id,
            'sop_title': sop.title,
            'content': sop.content,
            'source_type': 'sop_text'
        })

        for document in sop.documents:
            if not (document.extracted_text or '').strip():
                continue
            retrieval_input.append({
                'sop_id': sop.id,
                'sop_title': sop.title,
                'content': document.extracted_text,
                'source_type': 'document',
                'document_id': document.id,
                'document_title': document.title,
                'download_url': f"/sops/documents/{document.id}/download"
            })

    rag_output = run_rag(question, retrieval_input)
    answer = rag_output['answer']
    sources = rag_output['sources']

    user_id = int(get_jwt_identity())
    primary_sop_id = selected_sop.id if selected_sop else (sources[0]['sop_id'] if sources else sop_candidates[0].id)
    log = QnALog(
        question=question,
        answer=answer,
        sources=json.dumps(sources),
        user_id=user_id,
        sop_id=primary_sop_id
    )
    db.session.add(log)
    db.session.commit()

    top_source_owner = None
    if sources and sources[0].get('sop_id'):
        top_sop = SOP.query.get(sources[0]['sop_id'])
        top_source_owner = User.query.get(top_sop.owner_id) if top_sop else None
    elif selected_sop:
        top_source_owner = User.query.get(selected_sop.owner_id)

    return jsonify({
        "answer": answer,
        "sources": sources,
        "confidence": rag_output['confidence'],
        "sop_title": sources[0]['sop_title'] if sources else (selected_sop.title if selected_sop else 'Unknown SOP'),
        "sop_owner": top_source_owner.email if top_source_owner else 'Unknown'
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
        parsed_sources = []
        if log.sources:
            try:
                parsed_sources = json.loads(log.sources)
            except json.JSONDecodeError:
                parsed_sources = [{'sop_id': log.sop_id, 'sop_title': sop.title if sop else 'Unknown SOP', 'excerpt': log.sources, 'score': None}]

        payload.append({
            'id': log.id,
            'question': log.question,
            'answer': log.answer,
            'sources': parsed_sources,
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
    
    parsed_sources = []
    if log.sources:
        try:
            parsed_sources = json.loads(log.sources)
        except json.JSONDecodeError:
            parsed_sources = [{'sop_id': log.sop_id, 'sop_title': sop.title if sop else 'Unknown SOP', 'excerpt': log.sources, 'score': None}]

    return jsonify({
        'id': log.id,
        'question': log.question,
        'answer': log.answer,
        'sources': parsed_sources,
        'sop_title': sop.title if sop else 'Unknown SOP',
        'created_at': log.created_at.isoformat() if log.created_at else None
    }), 200
