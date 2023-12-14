from flask import Flask
import flask_jwt_extended
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from config import Config

# create flask app
app = Flask(__name__)
app.config.from_object(Config)

# initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = flask_jwt_extended.JWTManager(app)

# 블루프린트 등록
from app.routes import auth_routes, user_modify_routes
app.register_blueprint(auth_routes)
app.register_blueprint(user_modify_routes)
