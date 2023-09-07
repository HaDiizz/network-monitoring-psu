from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, session
from .. import forms
from flask_login import login_user, login_required, logout_user, current_user
from .. import models
import mongoengine as me
from ..utils import location_list, host_list, host_down_handler
from .. import oauth2
import datetime

module = Blueprint('site', __name__)

@module.app_context_processor
def account_context():
    return {'account': current_user}

@module.route('/host-down')
def host_down():
    host_down_handler()
    return "hello"

@module.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect('/admin/overview')
    hosts = host_list()
    if not hosts:
        hosts = []
    return render_template("index.html", title="หน้าหลัก", location_list=location_list(), host_list=hosts)

@module.route('/get-hosts')
def get_hosts():
    return jsonify(host_list())

@module.route('/get-locations')
def getLocations():
    location_data = []
    for location in location_list():
        location_data.append({
            "id": str(location.id),
            "name": location.name,
            "lat": location.lat,
            "lng": location.lng
        })
    return jsonify(location_data)

@module.route('/login')
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect('/admin/overview')
        else:
            return redirect('/')
    
    client = oauth2.oauth2_client
    redirect_uri = url_for("site.auth", _external=True)
    return client.psu_passport.authorize_redirect(redirect_uri)

@module.route('/auth')
def auth():
    
    client = oauth2.oauth2_client
    try:
        token = client.psu_passport.authorize_access_token()
    except Exception as e:
        print(e)
        return redirect(url_for("site.login"))
    print(token)
    session['user'] = token['userinfo']
    

    user = models.User.objects(
        me.Q(username=session['user'].get("username", ""))
        | me.Q(email=session['user'].get("email", ""))
    ).first()

    if not user:
        user = models.User(
            username=session['user'].get("username"),
            email=session['user'].get("email"),
            first_name=session['user'].get("first_name").title(),
            last_name=session['user'].get("last_name").title(),
            status="active",
        )
        if session['user']["username"].isdigit():
            user.role = "user"
    

    user.save()

    login_user(user)

    oauth2token = models.OAuth2Token(
        name=client.psu_passport.name,
        user=user,
        access_token=token.get("access_token"),
        token_type=token.get("token_type"),
        refresh_token=token.get("refresh_token", None),
        expires=datetime.datetime.utcfromtimestamp(token.get("expires_in")),
    )
    oauth2token.save()

    next_uri = session.get("next", None)
    if next_uri:
        session.pop("next")
        return redirect(next_uri)
    return redirect(url_for("site.index"))

@module.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user', None)
    return redirect(url_for('site.index'))

@module.route('/report', methods=["GET", "POST"])
def report():
    form = forms.ReportForm()
    if form.validate_on_submit():
        title = form.title.data
        detail = form.detail.data
        lat = form.lat.data
        lng = form.lng.data
        issue_category = form.issue_category.data
        if any(field == "" for field in [title, detail, lat, lng, issue_category]):
            flash("กรุณากรอกข้อมูล/ปักหมุดสถานที่ในแมพ", "error")
            return render_template("report.html", title="รายงานปัญหา", form=form)
        report = models.Report(
            title=title,
            detail=detail,
            lat=round(float(lat), 6),
            lng=round(float(lng), 6),
            reported_by=current_user,
            category=issue_category
        )
        report.save()
        flash("บันทึกสำเร็จ", "success")
        form.title.data = ""
        form.detail.data = ""
        form.lat.data = ""
        form.lng.data = ""
        form.issue_category.data = ""

    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect('/admin/overview')
    else:
        return redirect('/login')

    return render_template("report.html", title="รายงานปัญหา", form=form)
