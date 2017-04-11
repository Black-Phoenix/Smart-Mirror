import os

import httplib2
from flask import *
from googleapiclient import discovery

app = Flask(__name__)
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

#This file adds a new user
SECRET = os.getcwd() + '/Conf/client_secret.json'
home_dir = os.path.expanduser('~')
credential_dir = os.path.join(home_dir, '.credentials')
if not os.path.exists(credential_dir):
    os.makedirs(credential_dir)


def CreateOAuthFlow():
    """Create OAuth2.0 flow controller

    This controller can be used to perform all parts of the OAuth 2.0 dance
    including exchanging an Authorization code.

    Args:
      request: HTTP request to create OAuth2.0 flow for
    Returns:
      OAuth2.0 Flow instance suitable for performing OAuth2.0.
    """
    flow = client.flow_from_clientsecrets(SECRET, scope='https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/userinfo.profile')
    # Dynamically set the redirect_uri based on the request URL. This is extremely
    # convenient for debugging to an alternative host without manually setting the
    # redirect URI.
    flow.redirect_uri = "http://localhost:5000"
    return flow

def save_data(user_name, credentials):
    f = open("Conf/users.conf", "a+")
    f.write("\n" + user_name)
    f.close()
    id = int(sum(1 for line in open("Conf/users.conf", "r"))) - 1
    credential_path = os.path.join(credential_dir,
                                   'calendar-mirror-' + str(id) + '.json')
    store = Storage(credential_path)
    store.put(credentials)
    print(user_name)


@app.route("/")
def google_auth_page():
    code = request.args.get('code')
    if code == None:
        flow = CreateOAuthFlow()
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)
    else:
        print(code)
        flow = CreateOAuthFlow()
        auth_obj = flow.step2_exchange(code=code)
        print(auth_obj)
        http = auth_obj.authorize(httplib2.Http())
        service = discovery.build('plus', 'v1', http=http)
        mePerson = service.people().get(userId='me').execute(http=http)
        user_name = '%s' % mePerson['displayName']
        save_data(user_name, auth_obj)
        return "Successfully Added User"

def start():
    app.run()
start()