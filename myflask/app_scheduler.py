import pytz
import os
import requests
import atexit
from http import HTTPStatus
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler

class AppScheduler:
    def __init__(self):
        print('\nInitializing App Scheduler...\n')
        self.self_url = os.getenv("PORTFOLIO_URL")
        self.http_session = requests.session()

        self.scheduler = BackgroundScheduler()

        self.scheduler.add_job(
            self.sideProjectsAlive,
            trigger=CronTrigger(hour='7-21', minute='*/5', timezone=pytz.timezone('Asia/Kolkata')),
            id='sideProjectsAlive',
            name='Keep Others Alive',
        )

        self.scheduler.add_job(
            self.keepSelfAlive,
            'interval',
            minutes=5,
            id='keepSelfAlive',
            name='Keep Self Alive',
        )
        
        print("Done!\n")
        atexit.register(lambda: self.scheduler.shutdown())

    def keepSelfAlive(self):
        try:
            status = self.http_session.get(self.self_url).status_code
            if status != HTTPStatus.OK:
                self.http_session.post(f"{self.self_url}/send_email", json={
                    'subject': 'PORTFOLIO GOING DOWN',
                    'content': 'Failing to keep PORTFOLIO alive.'
                })
            print('🎶 Staying alive! 🎶')
        except Exception as e:
            print("Whoops!", e)

    def sideProjectsAlive(self):
        try:
            epapers_url = os.getenv("EPAPERS_HOSTNAME")
            epapers_status = self.http_session.get(epapers_url).status_code

            chatstomp_url = os.getenv("CHATSTOMP_URL")
            chatstomp_status = self.http_session.get(chatstomp_url).status_code

            if epapers_status != HTTPStatus.OK or chatstomp_status != HTTPStatus.OK:
                self.http_session.post(f"{self.self_url}/send_email", json={
                    'subject': 'SIDE PROJECTS GOING DOWN',
                    'content': f'Failing to keep EPAPERS - {epapers_url} and CHATSTOMP - {chatstomp_url} alive.'
                })
        except Exception as e:
            print("Whoops!", e)

    def start(self):
        self.scheduler.start()