# coding=utf-8
import sys
from importlib import reload

from flask import Flask, request, session, json, jsonify
from flask_cors import CORS, cross_origin

# Создаём приложение
from storage import userQueries, taskQueries
from storage.validation import userValidation, taskValidation
from entities.models import Task
from db.database import init_db, db_session

app = Flask(__name__)
CORS(app)

# Конфигурируем
# Устанавливаем ключ, необходимый для шифрования куки сессии
app.secret_key = b'newsecretkeyweb56gogogo'


# обработка запроса входа в систему зарегистрированного пользователя
@app.route('/api/login', methods=['GET'])
@cross_origin()
def set_login():
    login = request.args.get('user_login')
    password = request.args.get('user_password')
    error = None

    login = login.strip()
    # password = password.strip()

    code = 422
    if not login:
        error = "Требуется ввести логин!"
    elif not password:
        error = "Требуется ввести пароль!"

    user = None
    if error is None and login and password:
        user = userQueries.get_user_by_login(login)
        if not user:
            error = "Неверный пароль!"
        elif not userValidation.check_user_password(user, password):
            error = "Неверный пароль!"

    if error is None:
        session['user_id'] = user.id
        print("user_id = ", session['user_id'])
        code = 200
        return jsonify(json.dumps(user.serialize())), code

    return jsonify(error=error), code


# регистрация нового пользователя
@app.route('/registration', methods=['POST'])
@cross_origin()
def add_registration():
    json_request = request.get_json()
    login = json_request['login']
    password = json_request['password1']
    password2 = json_request['password2']

    login = login.strip()
    # password = password.strip()
    # password2 = password2.strip()

    error = None
    code = 422
    if not login:
        error = "Требуется ввести электронную почту!"
    elif not userValidation.validate_login(login):
        error = "Логин не должен содержать пробелов!"
    elif not password:
        error = "Требуется ввести пароль!"
    elif not userValidation.validate_password(password):
        error = "В пароле не должно быть символов пробела!"
    elif not password2:
        error = "Введите повтор пароля!"
    elif password != password2:
        error = "Пароли не совпадают!"

    user = None
    if error is None and login and password and password2:
        user = userQueries.get_user_by_login(login)
    if user:
        error = "Пользователь с таким email уже зарегистрирован!"

    if error is None:
        userQueries.add_user(login, password)
        user = userQueries.get_user_by_login(login)
        session['user_id'] = user.id
        print("user_id = ", session['user_id'])
        code = 200
        return jsonify(json.dumps(user.serialize())), code

    return jsonify(error=error), code


# получение списка to do текущего пользователя
@app.route('/api/todos', methods=['GET'])
@cross_origin()
def get_todos():
    try:
        user_id = int(request.args.get('user_id'))
    except ValueError:
        return jsonify(error='Доступ запрещён!'), 403

    if user_id != session['user_id']:
        return jsonify(error='Доступ запрещён!'), 403

    json_todos = json.dumps(Task.serialize_list(taskQueries.get_tasks_by_user_id(user_id)))
    return jsonify(json_todos), 200


# обработка запроса создания нового to do
@app.route('/api/todos', methods=['POST'])
def add_task():
    json_request = request.get_json()
    user_id = int(json_request['user_id'])

    if user_id != session['user_id']:
        return jsonify(error='Доступ запрещён!'), 403

    error = None
    code = 422
    title = json_request['title']
    description = json_request['description']
    completed = json_request['completed']

    if not title:
        error = "Необходимо ввести заголовок!"
    elif not taskValidation.validate_task_title(title):
        error = "Необходимо ввести заголовок!"
    elif taskQueries.get_task_by_title('', title, user_id):
        error = "Уже есть задача с таким заголовком!"

    if error is None:
        todo = taskQueries.add_task(user_id, title, description, completed)
        code = 200
        return jsonify(json.dumps(todo.serialize())), code
    return jsonify(error=error), code


# обработка запроса обновления конкретного to do
@app.route('/api/todos/<todo_id>', methods=['POST'])
def task_update(todo_id):
    json_request = request.get_json()
    user_id = int(json_request['user_id'])
    if user_id != session['user_id']:
        return jsonify(error='Доступ запрещён!'), 403

    error = None
    code = 422
    title = json_request['title']
    description = json_request['description']
    completed = json_request['completed']
    task = taskQueries.get_task_by_id(todo_id)
    if task is None:
        return jsonify(error="Попытка отредактировать несуществующее задание"), 404
    current_title = task.title

    if not title:
        error = "Необходимо ввести заголовок!"
    elif not taskValidation.validate_task_title(title):
        error = "Необходимо ввести заголовок!"
    elif taskQueries.get_task_by_title(current_title, title, user_id):
        error = "Уже есть задача с таким заголовком!"

    if error is None:
        todo = taskQueries.update_task(user_id, todo_id, title, description, completed)
        code = 200
        return jsonify(json.dumps(todo.serialize())), code
    return jsonify(error=error), code


# обработка запроса удаления конкретного to do
@app.route('/api/todos/delete', methods=['POST'])
@cross_origin()
def task_remove():
    json_request = request.get_json()
    user_id = int(json_request['user_id'])
    if user_id != session['user_id']:
        return jsonify(error='Доступ запрещён!'), 403

    todo_id = json_request['id']

    error = None
    code = taskQueries.remove_task(user_id, todo_id)
    if code == 404:
        error = 'Попытка удалить несуществующее задание'
    return jsonify(error=error), code


# обработка выхода из системы
@app.route('/api/logout', methods=['POST'])
@cross_origin()
def logout():
    session['user_id'] = None
    return jsonify(error=None), 200


# закрытие сессии БД после окончания работы
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == "__main__":
    reload(sys)
    init_db()
    app.run('localhost', 5000)
