from app.views.admin import admin_blueprint

@admin_blueprint.route("/setting")
def setting():
    return "admin setting"