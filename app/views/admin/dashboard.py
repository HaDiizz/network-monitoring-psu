from app.views.admin import admin_blueprint

@admin_blueprint.route("/dashboard")
def dashboard():
    return "admin dashboard"