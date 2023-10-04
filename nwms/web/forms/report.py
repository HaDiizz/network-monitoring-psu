from flask_wtf import FlaskForm
from wtforms import validators, StringField, SubmitField, HiddenField, TextAreaField, SelectField
from nwms import models

class ReportForm(FlaskForm):
    title = StringField("หัวข้อปัญหา", render_kw={'class': 'input input-bordered w-full', 'placeholder': 'หัวข้อ', 'maxlength': '100'}, validators=[validators.InputRequired()])
    issue_category = SelectField("ประเภทปัญหา", choices=[('', '-- โปรดเลือก --')], render_kw={'class': 'select select-bordered w-full max-w-xs'}, validators=[validators.InputRequired(message="กรุณาเลือกประเภทปัญหา")])
    detail = TextAreaField("รายละเอียด", render_kw={'class': 'textarea textarea-bordered w-full', 'placeholder': 'รายละเอียด (ปัญหา, สถานที่, ตึก, ชั้น)', 'maxlength': '300'}, validators=[validators.InputRequired()])
    lat = HiddenField("Latitude", render_kw={'class': 'input input-bordered w-full', 'placeholder': 'Latitude'})
    lng = HiddenField("Longitude", render_kw={'class': 'input input-bordered w-full', 'placeholder': 'Longitude'})
    submit = SubmitField("บันทึก", render_kw={'class': 'btn bg-primary hover:bg-secondary dark:bg-neutral text-white'})
    
    def __init__(self):
        super().__init__()
        self.categories = []
        categories = models.Category.objects().order_by("category_name")
        for category in categories:
            self.issue_category.choices.append((category.category_name, category.category_name))

class ReportFilterForm(FlaskForm):
    status = SelectField("Status", choices=[('ALL', 'ALL'), ('PENDING', 'PENDING'), ('CHECKING', 'CHECKING'), ('COMPLETED', 'COMPLETED'), ('REJECTED', 'REJECTED')], render_kw={'class': 'select select-bordered w-full max-w-xs'})
    search = SubmitField("ค้นหา", render_kw={'class': 'btn bg-primary hover:bg-secondary dark:bg-neutral text-white'})