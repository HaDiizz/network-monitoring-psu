from flask import redirect
from flask_login import current_user, LoginManager
from werkzeug.exceptions import Forbidden
from . import models

from functools import wraps

login_manager = LoginManager()


def init_acl(server):
    login_manager.init_app(server)
    login_manager.session_protection = "strong"
    login_manager.login_view = 'login'

def roles_required(*roles):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                # raise Forbidden()
                return redirect("/")

            for role in roles:
                if role == current_user.role:
                    return func(*args, **kwargs)
            raise Forbidden()

        return wrapped

    return wrapper


@login_manager.user_loader
def load_user(user_id):
    user = models.User.objects.with_id(user_id)
    return user