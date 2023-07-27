from flask_wtf import FlaskForm
from wtforms import validators, StringField, SubmitField, HiddenField, TextAreaField, SelectField

class ReportForm(FlaskForm):
    title = StringField("หัวข้อปัญหา", render_kw={'class': 'input input-bordered w-full', 'placeholder': 'หัวข้อ', 'maxlength': '100'}, validators=[validators.InputRequired()])
    detail = TextAreaField("รายละเอียด", render_kw={'class': 'textarea textarea-bordered w-full', 'placeholder': 'รายละเอียด (ปัญหา, สถานที่, ตึก, ชั้น)', 'maxlength': '300'}, validators=[validators.InputRequired()])
    lat = HiddenField("Latitude", render_kw={'class': 'input input-bordered w-full', 'placeholder': 'Latitude'})
    lng = HiddenField("Longitude", render_kw={'class': 'input input-bordered w-full', 'placeholder': 'Longitude'})
    submit = SubmitField("บันทึก", render_kw={'class': 'btn bg-primary hover:bg-secondary dark:bg-neutral text-white'})
    
class ReportFilterForm(FlaskForm):
    status = SelectField("Status", choices=[('ALL', 'ALL'), ('PENDING', 'PENDING'), ('CHECKING', 'CHECKING'), ('APPROVED', 'APPROVED'), ('REJECTED', 'REJECTED')], render_kw={'class': 'select select-bordered w-full max-w-xs'})
    search = SubmitField("ค้นหา", render_kw={'class': 'btn bg-primary hover:bg-secondary dark:bg-neutral text-white'})