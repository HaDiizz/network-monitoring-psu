from app import server
from app.helpers.api import host_down_handler
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

if __name__ == '__main__':
    with server.app_context():
        scheduler.add_job(host_down_handler, 'interval', seconds=60)
        scheduler.start()
        server.run(debug=True)