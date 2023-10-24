from flask import Flask, redirect, url_for, session, render_template, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import requests
import os
import json
import sqlite3
from sqlite3 import Error
import time
import threading

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

# Load the client credentials JSON file
key_path = 'google_client_credentials.json'  # File is in the same directory
with open(key_path) as key_file:
    client_credentials = json.load(key_file)

# Set up the Google OAuth2 flow
flow = Flow.from_client_config(
    client_credentials,
    scopes=['openid', 'email'],
    redirect_uri='https://cop4521.seasons-fm.com/newsfeed'
)

@app.route('/')
def index():
    if not session.get('credentials'):
        return redirect(url_for('login'))
    credentials = session.get('credentials')
    id_info = id_token.verify_oauth2_token(credentials, Request(), flow.client_config['client_id'])
    if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        return 'Access denied: Invalid issuer.'
    return 'Logged in as: ' + id_info['email']

@app.route('/login')
def login():
    authorization_url, state = flow.authorization_url(access_type='offline')
    session['state'] = state
    return redirect(authorization_url)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        # Handle the POST request for logging out (remove user credentials from the session)
        session.pop('credentials', None)
        return 'Logged out'
    else:
        # Handle the GET request (e.g., display a confirmation page or redirect)
        return 'Are you sure you want to log out?'

@app.route('/login/authorized')
def authorized():
    state = session['state']
    flow.fetch_token(authorization_response=request.url, state=state)
    session['credentials'] = flow.credentials.to_json()
    return redirect('https://cop4521.seasons-fm.com/newsfeed')

@app.route('/newsfeed')
def newsfeed():
    # Connect to the SQLite database
    conn = sqlite3.connect('hacker_news.db')
    cursor = conn.cursor()

    # Retrieve the last 10 news items from the database
    cursor.execute('SELECT title, url FROM news ORDER BY time DESC LIMIT 30')
    news_items = [{'title': row[0], 'url': row[1]} for row in cursor.fetchall()]

    # Close the database connection
    conn.close()
    user_email = "user@example.com"

    return render_template('html/newsfeed.html', news_items=news_items, user_email=user_email)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
