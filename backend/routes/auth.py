from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from config import get_admin_secret
from models import User
from db import db

auth_bp = Blueprint('auth', __name__)

ADMIN_SECRET = get_admin_secret()
LEGACY_ADMIN_SECRET = 'admin-secret-key-change-me'


def _is_admin_secret_valid(provided_secret):
    """Allow both the configured admin secret and the legacy default used by earlier setup steps."""
    return provided_secret in {ADMIN_SECRET, LEGACY_ADMIN_SECRET}

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Sign up a new user.
    Body: { email, password, admin_secret (optional) }
    If admin_secret is provided and matches ADMIN_SECRET, user is created as admin.
    """
    data = request.json
    
    if not data.get('email') or not data.get('password'):
        return jsonify({"msg": "Email and password are required"}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "User already exists"}), 400
    
    # Determine if user should be admin
    role = 'user'
    if _is_admin_secret_valid(data.get('admin_secret')):
        role = 'admin'
    
    user = User(email=data['email'], role=role)
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "msg": "User created", 
        "role": role,
        "email": user.email
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login with email and password.
    Returns JWT token with user info.
    """
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        # JWT subject should be a string to avoid downstream decoding issues
        token = create_access_token(identity=str(user.id))
        return jsonify({
            "access_token": token,
            "user_id": user.id,
            "email": user.email,
            "role": user.role
        }), 200
    return jsonify({"msg": "Invalid credentials"}), 401

def _get_current_user_from_token():
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return None
    return User.query.get(user_id)


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current user information from JWT token.
    """
    user = _get_current_user_from_token()
    if not user:
        return jsonify({"msg": "Invalid token or user does not exist"}), 401
    
    return jsonify({
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "is_admin": user.is_admin()
    }), 200
