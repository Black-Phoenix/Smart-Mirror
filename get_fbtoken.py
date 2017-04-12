import facebook as fb
import requests

app_id = '1999591750270524'
client_secret = "d3166755d7f0053694a0a07f6dfedc52"


def get_authentication_url():
    perms = ['read_page_mailboxes',
             'manage_pages',
             'publish_pages']
    canvas_url = 'http://localhost:8080/fb/success'
    fb_url = fb.auth_url(app_id=app_id, canvas_url=canvas_url, perms=perms)
    return fb_url


def short_to_long_term_token(code):
    url = "https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&"
    client_id = str(app_id)
    url += "client_id=" + client_id + "&"

    url += "client_secret=" + client_secret + "&"
    url += "fb_exchange_token=" + code
    url = url.strip()
    r = requests.get(url)
    contents = r.json()
    return contents['access_token']


def code_to_access_token(code):
    code = str(code)
    url = "https://graph.facebook.com/oauth/access_token?client_id=" + app_id + \
          "&redirect_uri=" + "http://localhost:8080/fb/success&client_secret=" + \
          client_secret + "&code=" + code
    r = requests.get(url)
    contents = r.json()
    access_token = contents['access_token']
    return access_token

