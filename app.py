from app import server

if __name__ == '__main__':
    with server.app_context():
        server.run(debug=True)