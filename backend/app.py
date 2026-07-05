from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from routes.auth import auth_bp
from routes.sops import sops_bp
from routes.questions import questions_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/sop_db'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret'

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Register routes
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(sops_bp, url_prefix='/sops')
app.register_blueprint(questions_bp, url_prefix='/questions')

if __name__ == '__main__':
    app.run(debug=True)
