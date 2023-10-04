from flask_wtf import FlaskForm
from wtforms import validators, StringField, SubmitField, FloatField

class LocationForm(FlaskForm):
    name = StringField("ชื่อสถานที่", render_kw={'class': 'input input-bordered w-full', 'placeholder': 'ชื่อสถานที่', 'maxlength': '100'}, validators=[validators.InputRequired()])
    lat = FloatField("Latitude", render_kw={'class': 'input input-bordered w-full', 'placeholder': 'Latitude'}, validators=[validators.InputRequired()])
    lng = FloatField("Longitude", render_kw={'class': 'input input-bordered w-full', 'placeholder': 'Longitude'}, validators=[validators.InputRequired()])
    submit = SubmitField("เพิ่มข้อมูล", render_kw={'class': 'btn bg-primary hover:bg-secondary dark:bg-neutral text-white'})
