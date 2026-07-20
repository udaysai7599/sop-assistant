import os
import sqlite3
from pathlib import Path
from datetime import timedelta
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
base_dir = Path(__file__).resolve().parent
workspace_root = base_dir.parent
legacy_root_instance = workspace_root / 'instance' / 'sop_db.sqlite'
legacy_backend_instance = base_dir / 'instance' / 'sop_db.sqlite'

if os.getenv('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
elif legacy_root_instance.exists():
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{legacy_root_instance.as_posix()}"
else:
    legacy_backend_instance.parent.mkdir(parents=True, exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{legacy_backend_instance.as_posix()}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'sop-assistant-super-secret-key-2026')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_HOURS', '8')))

CORS(app, resources={r'/*': {'origins': '*'}})
db.init_app(app)
jwt = JWTManager(app)

# Register routes
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(sops_bp, url_prefix='/sops')
app.register_blueprint(questions_bp, url_prefix='/questions')
app.register_blueprint(answers_bp, url_prefix='/answers')


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
        db.create_all()
        ensure_sqlite_column('user', 'role', "VARCHAR(20)", "'user'")
    app.run(host='0.0.0.0', port=5000, debug=True)
