import os
import sys
import requests
import json
import db

from flask import Flask, render_template, url_for, redirect, request
from dotenv import load_dotenv
from flask_login import LoginManager, current_user, login_user
from oauthlib.oauth2 import WebApplicationClient
from user import User
from user_repo import fetch_user, ensure_user_exists

load_dotenv()

CLIENT_ID = os.environ.get("CLIENT_ID", None)
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", None)
SECRET_KEY = os.environ.get("SECRET_KEY", None)

app = Flask(__name__)
app.secret_key = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
db.init_app(app)

client = WebApplicationClient(CLIENT_ID)


@login_manager.user_loader
def load_user(user_id):
    return fetch_user(user_id)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html', user=current_user)
    else:
        return render_template('login.html')

@app.route('/login')
def login():
    return redirect(client.prepare_request_uri('https://github.com/login/oauth/authorize'))

@app.route('/login/callback')
def callback():
    # 1) Parse the response from GitHub to find the temporary code
    code = request.args.get('code')
    # 2) Use that code to collect an access token from GitHub
    token_url, headers, body = client.prepare_token_request('https://github.com/login/oauth/access_token', code=code)
    headers['Accept'] = 'application/json' # Get JSON response rather than byte (see default response below)
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(CLIENT_ID, CLIENT_SECRET),
    )
    '''
    Github: By default, the response takes the following form:
    access_token=e72e16c7e42f292c6912e7710c838347ae178b4a&token_type=bearer
    '''
    # print(token_response.content, file=sys.stdout) # b'access_token=d9d3cfc73aede69ad7b0e4b7faa11b86873728d9&scope=&token_type=bearer'
    '''
    Bytes literals are always prefixed with 'b' or 'B'; they produce an instance of the 
    bytes type instead of the str type. Convert with the decode function:
    '''
    # text = token_response.content.decode("utf-8")
    client.parse_request_body_response(json.dumps(token_response.json()))
    # 3) Use the access token to access the data we want
    uri, headers, body = client.add_token('https://api.github.com/user')
    user_response = requests.get(uri, headers=headers).json()
    # 4) Construct a new user object using that data
    user = User(
        user_id=user_response['id'],
        name=user_response['login'],
        profile_image=user_response['avatar_url']
    )
    ensure_user_exists(user)

    login_user(user)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
