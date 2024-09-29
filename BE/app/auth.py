from flask import g
from flask_httpauth import HTTPBasicAuth
from .config import Config
from .model.user import User

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if not Config.ENABLE_AUTH:
        return True
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        g.current_user = user
        return True
    return False