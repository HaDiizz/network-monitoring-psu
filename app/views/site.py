from flask import Blueprint, render_template, redirect, url_for
from .. import forms
from flask_login import login_user, login_required, logout_user, current_user
from .. import models
import mongoengine as me

module = Blueprint('site', __name__)

@module.app_context_processor
def account_context():
    return {'account': current_user}

@module.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect('/admin/overview')
    return render_template("index.html", title="หน้าหลัก")

@module.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect('/admin/overview')
        else:
            return redirect('/')
    form = forms.login.LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = models.User.objects(me.Q(username=username) & me.Q(password=password)).first()
        if user:
            login_user(user, remember=True)
            return redirect('/')
    return render_template("login.html", title="เข้าสู่ระบบ", form=form)

@module.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('site.index'))

@module.route('/report', methods=["GET", "POST"])
def report():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect('/admin/overview')
    else:
        return redirect('/login')
    form = forms.report.ReportForm()
    if form.validate_on_submit():
        topic = form.topic.data
        detail = form.detail.data
        lat = form.lat.data
        lng = form.lng.data
        print("topic", topic)
        print("detail", detail)
        print("lat", lat)
        print("lng", lng)
    return render_template("report.html", title="รายงานปัญหา", form=form)