from flask import Blueprint

site_blueprint = Blueprint('site', __name__)

@site_blueprint.route('/')
def index():
    return "home"

@site_blueprint.route('/login')
def login():
    return "login"

@site_blueprint.route('/logout')
def logout():
    return "logout"

@site_blueprint.route('/forgotPassword')
def forgotPassword():
    return "forgotPassword"

@site_blueprint.route('/resetPassword')
def resetPassword():
    return "resetPassword"

@site_blueprint.route('/report')
def report():
    return "report"