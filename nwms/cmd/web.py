from nwms import web


def main():
    options = web.get_program_options()
    app = web.create_app()

    app.run(debug=options.debug, host=options.host, port=int(options.port))