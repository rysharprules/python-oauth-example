import os

from flask import Flask, render_template, url_for, redirect
from dotenv import load_dotenv
from flask_login import LoginManager, current_user, login_user
from oauthlib.oauth2 import WebApplicationClient

import db
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
    # Redirect the user to GitHub's OAuth Login Page
    pass


@app.route('/login/callback')
def callback():
    # 1) Parse the response from GitHub to find the temporary code
    # 2) Use that code to collect an access token from GitHub
    # 3) Use the access token to access the data we want
    # 4) Construct a new user object using that data

    user = None  # replace this line!!

    ensure_user_exists(user)

    login_user(user)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
