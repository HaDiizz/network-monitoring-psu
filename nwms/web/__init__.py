# from flask import Flask
# import os
# from dotenv import load_dotenv
# from . import models
# from . import acl
# from . import caches
# from datetime import timedelta
# from . import oauth2

# load_dotenv()

# server = Flask(__name__)
# server.config['SECRET_KEY'] = os.environ['SECRET_KEY']
# server.config['CACHE_TYPE'] = 'SimpleCache'
# server.template_folder = 'templates'
# server.config['SESSION_COOKIE_NAME'] = 'psu-passport-login-session'
# server.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
# models.init_mongoengine(server)
# acl.init_acl(server)
# caches.init_cache(server)
# oauth2.init_oauth(server)

# from app.views import admin, site
# server.register_blueprint(admin.admin_module)
# server.register_blueprint(site.module)

import optparse

from flask import Flask

from nwms import models
from nwms.web import views
from nwms.web import acl
from nwms.web import oauth2

app = Flask(__name__)


def create_app():
    app.config.from_object("nwms.default_settings")
    app.config.from_envvar("NWMS_SETTINGS", silent=True)

    models.init_db(app)
    views.register_blueprint(app)
    acl.init_acl(app)
    oauth2.init_oauth(app)

    return app


def get_program_options(default_host="127.0.0.1", default_port="8000"):
    """
    Takes a flask.Flask instance and runs it. Parses
    command-line flags to configure the app.
    """

    # Set up the command-line options
    parser = optparse.OptionParser()
    parser.add_option(
        "-H",
        "--host",
        help="Hostname of the Flask app " + "[default %s]" % default_host,
        default=default_host,
    )
    parser.add_option(
        "-P",
        "--port",
        help="Port for the Flask app " + "[default %s]" % default_port,
        default=default_port,
    )

    # Two options useful for debugging purposes, but
    # a bit dangerous so not exposed in the help message.
    parser.add_option(
        "-c", "--config", dest="config", help=optparse.SUPPRESS_HELP, default=None
    )
    parser.add_option(
        "-d", "--debug", action="store_true", dest="debug", help=optparse.SUPPRESS_HELP
    )
    parser.add_option(
        "-p",
        "--profile",
        action="store_true",
        dest="profile",
        help=optparse.SUPPRESS_HELP,
    )

    options, _ = parser.parse_args()

    # If the user selects the profiling option, then we need
    # to do a little extra setup
    if options.profile:
        from werkzeug.middleware.profiler import ProfilerMiddleware

        app.config["PROFILE"] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
        options.debug = True

    return options