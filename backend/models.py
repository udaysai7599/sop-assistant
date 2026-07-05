from db import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    sops = db.relationship('SOP', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    sops = db.relationship('SOP', backref='department', lazy=True)

class SOP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    qna_logs = db.relationship('QnALog', backref='sop', lazy=True)

class QnALog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    sources = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sop_id = db.Column(db.Integer, db.ForeignKey('sop.id'))
