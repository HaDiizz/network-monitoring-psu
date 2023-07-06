from app.views.admin import admin_blueprint

@admin_blueprint.route("/management")
def management():
    return "admin management"