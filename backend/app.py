import os
import sqlite3
from pathlib import Path
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import get_app_host, get_app_port, get_database_uri, get_flask_debug_mode, get_jwt_secret_key
from db import db
from routes.auth import auth_bp
from routes.sops import sops_bp
from routes.questions import questions_bp
from routes.answers import answers_bp
from routes.documents import documents_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = get_jwt_secret_key()

CORS(app, resources={r'/*': {'origins': '*'}})
db.init_app(app)
jwt = JWTManager(app)

# Register routes
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(sops_bp, url_prefix='/sops')
app.register_blueprint(questions_bp, url_prefix='/questions')
app.register_blueprint(answers_bp, url_prefix='/answers')
app.register_blueprint(documents_bp, url_prefix='/documents')


def ensure_sqlite_column(table_name, column_name, column_type='VARCHAR(20)', default_value="'user'"):
    uri = app.config['SQLALCHEMY_DATABASE_URI']
    if not uri.startswith('sqlite:///'):
        return
    db_path = uri.replace('sqlite:///', '')
    if db_path == ':memory:':
        return
    db_path = os.path.abspath(db_path)
    if not os.path.exists(db_path):
        return
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info('{table_name}')")
        columns = [row[1] for row in cur.fetchall()]
        if column_name not in columns:
            cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} DEFAULT {default_value}")
            conn.commit()


if __name__ == '__main__':
    with app.app_context():
        # Ensure database directory exists
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            db_path = os.path.abspath(db_path)
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        db.create_all()
        ensure_sqlite_column('user', 'role', "VARCHAR(20)", "'user'")
    app.run(host=get_app_host(), port=get_app_port(), debug=get_flask_debug_mode())
