from requests_oauthlib import OAuth2Session
import settings
import os
from threading import Thread

from threading import Thread
from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify
from crawler import get_extra_data

app = Flask(__name__)

gl_state = ''
@app.route("/")
def login():
    global gl_state

    print 'login', settings.client_id
    github = OAuth2Session(settings.client_id)
    authorization_url, state = github.authorization_url(settings.authorization_base_url)
    gl_state = state

    print authorization_url
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    print request.url
    global gl_state

    github = OAuth2Session(settings.client_id)
    token = github.fetch_token(settings.token_url, client_secret=settings.client_secret,
                               authorization_response=request.url)

    t = Thread(target = get_extra_data, args = (github,))
    t.start()


    t = Thread(target = get_extra_data, args = (github))
    t.start()

    return 'crawling in the process'


if __name__ == '__main__':
    os.environ['DEBUG'] = '1'
    app.run(debug = True)