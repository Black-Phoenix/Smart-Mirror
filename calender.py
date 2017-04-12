from __future__ import print_function

import calendar

import math
from pytz import timezone

import httplib2
import os

from apiclient import discovery
from iso8601 import iso8601
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import datetime
import time

try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json

class Calender:
    def __init__(self, id):
        self.SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
        self.CLIENT_SECRET_FILE = '/Conf/client_secret.json'
        self.APPLICATION_NAME = 'Smart Mirror'
        self.events = []
        self.last_update = 0
        self.id = id
        self.update_tasks()
        self.selected_event = False
        self.calender_selected_event = 0
        self.updating = False

    def fix_time(self, events):
        for i in events:
            if "dateTime" in i["start"]:
                timestamp = i["start"]["dateTime"]
            elif "date" in i["start"]:
                timestamp = i["start"]["date"]
            i["start"] = math.ceil((iso8601.parse_date(timestamp) - datetime.datetime.now(
                timezone('Asia/Calcutta'))).total_seconds() / 3600)
            if "dateTime" in i["end"]:
                timestamp = i["end"]["dateTime"]
            elif "date" in i["end"]:
                timestamp = i["end"]["date"]
            i["end"] = math.ceil((iso8601.parse_date(timestamp) - datetime.datetime.now(
                timezone('Asia/Calcutta'))).total_seconds() / 3600)
        return events

    def fix_text(self, events):
        for i in events:
            if "summary" not in i:
                i["summary"] = "No Title"
        return events

    def get_credentials(self):
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        for i in range(2):
            credential_path = os.path.join(credential_dir,
                                           'calendar-mirror-' + str(self.id) + '.json')

            store = Storage(credential_path)
            credentials = store.get()
            if not credentials or credentials.invalid:
                flow = client.flow_from_clientsecrets(os.getcwd() + self.CLIENT_SECRET_FILE, self.SCOPES)
                flow.user_agent = self.APPLICATION_NAME
                if flags:
                    credentials = tools.run_flow(flow, store, flags)
                else:  # Needed only for compatibility with Python 2.6
                    credentials = tools.run(flow, store)
                print('Storing credentials to ' + credential_path)
        return credentials

    def fix(self, events):
        self.fix_text(events)
        self.fix_time(events)
        return events

    def update_tasks(self):
        if abs(self.last_update - calendar.timegm(time.gmtime())) > 60:
            self.updating = True
            credentials = self.get_credentials()
            http = credentials.authorize(httplib2.Http())
            service = discovery.build('calendar', 'v3', http=http)
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            eventsResult = service.events().list(
                calendarId='primary', timeMin=now, maxResults=20, singleEvents=True,
                orderBy='startTime').execute()
            events = eventsResult.get('items', [])
            self.events = self.fix(events)
            self.last_update = calendar.timegm(time.gmtime())
        self.updating = False

    def old_get_cred(self):
        def get_credentials(self):
            home_dir = os.path.expanduser('~')
            credential_dir = os.path.join(home_dir, '.credentials')
            if not os.path.exists(credential_dir):
                os.makedirs(credential_dir)
            for i in range(2):
                credential_path = os.path.join(credential_dir,
                                               'calendar-mirror-' + str(self.id) + '.json')

                store = Storage(credential_path)
                credentials = store.get()
                if not credentials or credentials.invalid:
                    flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
                    flow.user_agent = self.APPLICATION_NAME
                    if flags:
                        credentials = tools.run_flow(flow, store, flags)
                    else:  # Needed only for compatibility with Python 2.6
                        credentials = tools.run(flow, store)
                    print('Storing credentials to ' + credential_path)
            return credentials
