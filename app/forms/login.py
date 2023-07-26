from flask_wtf import FlaskForm
from wtforms import validators, StringField, SubmitField, PasswordField

class LoginForm(FlaskForm):
    username = StringField("Username", render_kw={'class': 'input input-bordered w-full'}, validators=[validators.InputRequired()])
    password = PasswordField("Password", render_kw={'class': 'input input-bordered w-full'}, validators=[validators.InputRequired()])
    submit = SubmitField("เข้าสู่ระบบ")