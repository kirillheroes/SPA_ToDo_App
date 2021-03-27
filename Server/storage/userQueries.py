from entities.models import User
from werkzeug.security import generate_password_hash
from db.database import db_session


# добавление нового пользователя в БД
def add_user(login, password):
    db_session.add(User(None, login, generate_password_hash(password, salt_length=64)))
    db_session.commit()


# получение пользователя по id
def get_user_by_id(user_id):
    return User.query.filter(User.id == user_id).first()


# получение пользователя по логину
def get_user_by_login(login):
    return User.query.filter(User.login == login).first()


# получение всех пользователей
def get_users():
    return User.query


