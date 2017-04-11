import os

from flask import *
app = Flask(__name__)
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

#This file adds a new user

def CreateOAuthFlow():
    """Create OAuth2.0 flow controller

    This controller can be used to perform all parts of the OAuth 2.0 dance
    including exchanging an Authorization code.

    Args:
      request: HTTP request to create OAuth2.0 flow for
    Returns:
      OAuth2.0 Flow instance suitable for performing OAuth2.0.
    """
    flow = client.flow_from_clientsecrets(os.getcwd() + '/Conf/client_secret.json', scope='https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/userinfo.profile')
    # Dynamically set the redirect_uri based on the request URL. This is extremely
    # convenient for debugging to an alternative host without manually setting the
    # redirect URI.
    flow.redirect_uri = "http://localhost:5000"
    return flow

@app.route("/")
def google_auth_page():
    code = request.args.get('code')
    if code == None:
        flow = CreateOAuthFlow()
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)
    else:
        print(code)
        auth_obj = flow.step2_exchange(code=code)
        "https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token=youraccess_token"
        return "Successfully Added User"

def start():
    app.run()
