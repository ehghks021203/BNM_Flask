from app import app
from .auth import auth_routes
from .user_modify import user_modify_routes

# 다른 모듈에서 사용할 수 있도록 Bcrypt 객체 생성
