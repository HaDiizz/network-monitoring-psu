from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, session, request
from nwms.web import forms
from flask_login import login_user, login_required, logout_user, current_user
from nwms import models
import mongoengine as me
from nwms.web.helpers.utils import location_list
from nwms.web.helpers.api import host_list, get_host_markers
from nwms.web import oauth2
import datetime


module = Blueprint('site', __name__)


@module.app_context_processor
def account_context():
    return {'account': current_user}


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
    return jsonify(get_host_markers())


@module.route('/get-host/<string:host_id>')
def get_host(host_id):
    try:
        times_list = []
        status_list = []
        data_filter = []
        host_list_ids = []
        now = datetime.datetime.now()
        selected_month = now.month
        selected_year = now.year
        selected_date = now.day
        host = models.Host.objects(
            host_id=host_id, month=selected_month, year=selected_year).first()
        if host:
            for host in host.host_list:
                host_list_ids.append(host["id"])
            query = models.HostList.objects(id__in=host_list_ids)
            query_host_list = query.all()

            for hour in range(24):
                for minute in range(0, 60, 10):
                    time_str = f"{hour:02d}:{minute:02d}"
                    times_list.append(time_str)

            for item in query_host_list:
                created_date = item["created_date"]
                day = created_date.day
                month = created_date.month
                year = created_date.year
                if day == selected_date and month == selected_month and year == selected_year:
                    data_filter.append(item)

            for i in times_list:
                status_list.append(1)

            for item in data_filter:
                last_state = item["last_state"]
                time_add = item["created_date"]
                if last_state != -1 :
                    time_hour = time_add.hour
                    time_minutes = time_add.minute
                    time_hour = time_hour * 6
                    time_minutes = int(time_minutes / 10)
                    time_down = int(item["minutes"] / 10)

                    start_time = time_hour + time_minutes
                    end_time = start_time + time_down

                else :
                    time_hour = time_add.hour
                    time_minutes = time_add.minute
                    time_hour = time_hour * 6
                    time_minutes = int(time_minutes / 10)
                    start_time = time_hour + time_minutes

                    my_datetime = datetime.datetime.now()
                    hour = int(my_datetime.strftime("%H"))
                    minute = int(my_datetime.strftime("%M"))
                    hour = hour * 6
                    minute = int(minute / 10)
                    end_time = hour + minute

                for i in range(start_time, end_time + 1):
                    status_list[i] = 0
                    

            if data_filter:
                my_datetime = datetime.datetime.now()
                hour = int(my_datetime.strftime("%H"))
                minute = int(my_datetime.strftime("%M"))
                hour = hour * 6
                minute = int(minute / 10)
                start_time = hour + minute
                end_time = len(status_list)
                
                for i in range(start_time, end_time):
                    status_list[i] = ""

            if not data_filter:
                if len(query_host_list) != 0:

                    last_state = query_host_list[len(
                        query_host_list)-1]["last_state"]
                    if last_state == -1:
                        for i in range(0, 144):
                            status_list[i] = 0
                            
            
            if not data_filter:
                my_datetime = datetime.datetime.now()
                hour = int(my_datetime.strftime("%H"))
                minute = int(my_datetime.strftime("%M"))
                hour = hour * 6
                minute = int(minute / 10)
                start_time = hour + minute
                end_time = len(status_list)

                for i in range(start_time, end_time):
                    status_list[i] = ""

            
            x_values = times_list
            y_values = status_list

            return jsonify(x_values, y_values)
        else:
            return jsonify({"error": "Host not found"}), 404
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


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
    scheme = request.environ.get("CONF_URL", "http")
    redirect_uri = url_for("site.auth", _external=True, _scheme=scheme)
    return client.psu_passport.authorize_redirect(redirect_uri)


@module.route('/auth')
def auth():

    client = oauth2.oauth2_client
    try:
        token = client.psu_passport.authorize_access_token()
    except Exception as e:
        return redirect(url_for("site.login"))
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
    session.clear()
    client = oauth2.oauth2_client
    remote = client.psu_passport
    logout_url = f"{ remote.server_metadata.get('end_session_endpoint') }?redirect={ request.scheme }://{ request.host }"
    if logout_url:
        return redirect(logout_url)

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

    if not current_user.is_authenticated:
        return redirect('/login')

    return render_template("report.html", title="รายงานปัญหา", form=form)


@module.route('/history', methods=["GET", "POST"])
def report_history():
    if not current_user.is_authenticated:
        return redirect('/login')
    reports = models.Report.objects(reported_by=current_user.id)
    return render_template("reportHistory.html", title="ประวัติรายงานปัญหา", reports=reports)
