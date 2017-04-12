import os

import httplib2
import numpy as np
from flask import *
from googleapiclient import discovery
import get_fbtoken
from oauth2client import client
import cv2
import posts
from oauth2client.file import Storage
from PIL import Image

# This file adds a new user
app = Flask(__name__, template_folder='templates')
SECRET = os.getcwd() + '/Conf/client_secret.json'
home_dir = os.path.expanduser('~')
user_conf = "Conf/users.conf"
credential_dir = os.path.join(home_dir, '.credentials')
if not os.path.exists(credential_dir):
    os.makedirs(credential_dir)

ALLOWED_EXTENSIONS = set(['jpg', 'png'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def CreateOAuthFlow():
    """Create OAuth2.0 flow controller

    This controller can be used to perform all parts of the OAuth 2.0 dance
    including exchanging an Authorization code.

    Args:
      request: HTTP request to create OAuth2.0 flow for
    Returns:
      OAuth2.0 Flow instance suitable for performing OAuth2.0.
    """
    flow = client.flow_from_clientsecrets(SECRET,
                                          scope='https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/userinfo.profile')
    # Dynamically set the redirect_uri based on the request URL. This is extremely
    # convenient for debugging to an alternative host without manually setting the
    # redirect URI.
    flow.redirect_uri = "http://localhost:8080"
    return flow


def find_id(path):
    id = int(sum(1 for line in open(path, "r")))
    return id


def fix_images(id):
    image_paths = [os.path.join("test/", f) for f in os.listdir("test/")]
    cascPath = "Conf/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascPath)
    i = 0
    for image_path in image_paths:
        # Read the image and convert to grayscale
        image_pil = Image.open(image_path).convert('L')
        # Convert the image format into numpy array
        image = np.array(image_pil, 'uint8')
        # Get the label of the image
        faces = faces = faceCascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30),
                                                     flags=cv2.CASCADE_SCALE_IMAGE)
        # If face is detected, append the face to images and the label to labels
        for (x, y, w, h) in faces:
            cv2.imwrite("img/faces/" + str(id) + "." + str(i) + ".jpg", image[y:y + h, x:x + w])
            i += 1


def save_data(user_name, credentials):
    id = find_id(user_conf)
    f = open("Conf/users.conf", "a+")
    f.write(user_name + "\n")
    f.close()
    credential_path = os.path.join(credential_dir,
                                   'calendar-mirror-' + str(id) + '.json')
    store = Storage(credential_path)
    store.put(credentials)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['id'] = find_id(user_conf)
            session.modified = True
            print(find_id(user_conf))
            return redirect("/")
    return render_template('login.html', error=error)


@app.route("/")
def google_auth_page():
    code = request.args.get('code')
    if 'id' not in session and code == None:
        return redirect('/login')
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
        return redirect(get_fbtoken.get_authentication_url())


@app.route("/fb/success")
def facebook_success():
    code = request.args.get('code')
    if code == None:
        return redirect("/")
    else:
        id = request.args.get('id')
        access_token_short = get_fbtoken.code_to_access_token(code)
        final_access_token = get_fbtoken.short_to_long_term_token(access_token_short)
        print(final_access_token)
        print(posts.get_posts(final_access_token))
        f = open("Conf/facebook/" + str(id) + ".conf", "w")
        f.write(final_access_token)
        return render_template("images.html")


@app.route("/upload", methods=["POST"])
def upload_images():
    uploaded_files = request.files.getlist("file[]")
    print(uploaded_files)
    inc = 0
    id = find_id(user_conf) - 1
    for file in uploaded_files:
        file.save(os.path.join(os.getcwd() + "/test", str(id) + "." + str(inc)))
        inc += 1
    fix_images(id)
    session["id"] = id + 1
    # os.popen('rm -f ./test/*')
    return "Successfully Added User"


def start():
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='127.0.0.1', port=8080)

if __name__ == '__main__':
    start()
