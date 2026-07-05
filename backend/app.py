import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from db import db
from routes.auth import auth_bp
from routes.sops import sops_bp
from routes.questions import questions_bp
from routes.answers import answers_bp

app = Flask(__name__)
# Use DATABASE_URL if provided, otherwise fall back to sqlite for local dev
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///sop_db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'sop-assistant-super-secret-key-2026')

CORS(app, resources={r'/*': {'origins': '*'}})
db.init_app(app)
jwt = JWTManager(app)

# Register routes
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(sops_bp, url_prefix='/sops')
app.register_blueprint(questions_bp, url_prefix='/questions')
app.register_blueprint(answers_bp, url_prefix='/answers')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
