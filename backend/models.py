from db import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)  # 'admin' or 'user'
    sops = db.relationship('SOP', backref='owner', lazy=True, cascade='all, delete-orphan')
    qna_logs = db.relationship('QnALog', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    sops = db.relationship('SOP', backref='department', lazy=True)

class SOP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    qna_logs = db.relationship('QnALog', backref='sop', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('SOPDocument', backref='sop', lazy=True, cascade='all, delete-orphan')


class SOPDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    extracted_text = db.Column(db.Text)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sop_id = db.Column(db.Integer, db.ForeignKey('sop.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

class QnALog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    sources = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sop_id = db.Column(db.Integer, db.ForeignKey('sop.id'), nullable=False)
