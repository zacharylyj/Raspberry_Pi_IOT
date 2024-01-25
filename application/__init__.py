from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

# create the Flask app
app = Flask(__name__)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)
# load configuration from config.cfg
app.config.from_pyfile("config.cfg")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# new method for SQLAlchemy version 3 onwards
with app.app_context():
    db.init_app(app)
    from .models import User, History

    db.create_all()
    db.session.commit()
    print("Created Database!")

from application import routes
