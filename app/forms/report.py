from flask_wtf import FlaskForm
from wtforms import validators, StringField, SubmitField, HiddenField, TextAreaField

class ReportForm(FlaskForm):
    topic = StringField("หัวข้อปัญหา", render_kw={'class': 'input input-bordered w-full'}, validators=[validators.InputRequired()])
    detail = TextAreaField("รายละเอียด", render_kw={'class': 'input input-bordered w-full', 'maxlength': '300'}, validators=[validators.InputRequired()])
    lat = HiddenField("Latitude", render_kw={'class': 'input input-bordered w-full'}, validators=[validators.InputRequired()])
    lng = HiddenField("Longitude", render_kw={'class': 'input input-bordered w-full'}, validators=[validators.InputRequired()])
    submit = SubmitField("บันทึก")