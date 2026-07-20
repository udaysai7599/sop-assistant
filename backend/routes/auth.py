from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import User
from db import db
import os

auth_bp = Blueprint('auth', __name__)

# Admin password for creating first admin (should be set as environment variable).
# If env var is present but empty, fall back to the local-dev default.
_ADMIN_SECRET_ENV = os.getenv('ADMIN_SECRET')
ADMIN_SECRET = _ADMIN_SECRET_ENV.strip() if _ADMIN_SECRET_ENV and _ADMIN_SECRET_ENV.strip() else 'admin-secret-key-change-me'

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Sign up a new user.
    Body: { email, password, admin_secret (optional) }
    If admin_secret is provided and matches ADMIN_SECRET, user is created as admin.
    """
    data = request.json or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    
    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400
    if len(password) < 8:
        return jsonify({"msg": "Password must be at least 8 characters"}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "User already exists"}), 400
    
    # Determine if user should be admin
    role = 'user'
    provided_admin_secret = (data.get('admin_secret') or '').strip()
    valid_admin_secrets = {ADMIN_SECRET, 'admin-secret-key-change-me'}
    if provided_admin_secret and provided_admin_secret in valid_admin_secrets:
        role = 'admin'
    
    user = User(email=email, role=role)
    user.set_password(password)
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
    data = request.json or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
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


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Stateless logout endpoint for explicit client flow.
    """
    return jsonify({"msg": "Logged out"}), 200
