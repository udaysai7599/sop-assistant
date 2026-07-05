from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    user = User(email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "User created"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        token = create_access_token(identity=user.id)
        return jsonify(access_token=token)
    return jsonify({"msg": "Invalid credentials"}), 401
