from werkzeug.security import check_password_hash


def check_user_password(user, password):
    return check_password_hash(user.password, password)


def validate_login(login):
    stop_chars = set(' ')
    return not any((c in stop_chars) for c in login)


def validate_password(password):
    stop_chars = set(' ')
    return not any((c in stop_chars) for c in password)
