from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    main_nok_id = db.Column(db.Integer, db.ForeignKey('main_nok.id'), nullable=False)
    user_id = db.Column(db.String(20), nullable=False)
    user_pw = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    birthday = db.Column(db.DateTime)
    gender = db.Column(db.String(1), nullable=False)
    relation = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    blood_type = db.Column(db.String(2), nullable=True)
    chronic_illness = db.Column(db.BLOB, nullable=True)
    hometown = db.Column(db.String(100), nullable=True)
    details = db.Column(db.String(500), nullable=True)
    last_chat_group = db.Column(db.Integer, nullable=False, default=0)
    is_first = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<User {self.user_id}>"

class MainNok(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nok_id = db.Column(db.String(20), nullable=False)
    nok_pw = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    birthday = db.Column(db.DateTime, nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    tell = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<NokUser {self.nok_id}>"

class UserFavoriteFood(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    favorite_food = db.Column(db.String(20))

    def __repr__(self):
        return f"<UserFavoriteFood {self.id}>"

class UserFavoriteMusic(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    favorite_music = db.Column(db.String(50))

    def __repr__(self):
        return f"<UserFavoriteMusic {self.id}>"

class UserFavoriteSeason(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    favorite_season = db.Column(db.String(2))

    def __repr__(self):
        return f"<UserFavoriteSeason {self.id}>"

class UserPastJob(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    past_job = db.Column(db.String(20))

    def __repr__(self):
        return f"<UserPastJob {self.id}>"

class UserPet(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pet = db.Column(db.String(20))

    def __repr__(self):
        return f"<UserPet {self.id}>"

class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver = db.Column(db.String(20), nullable=False)
    chat_group_id = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ChatLog {self.id}>"

class MemoryTestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    correct = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<MemoryTestResult {self.id}>"