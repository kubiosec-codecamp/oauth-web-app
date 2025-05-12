from flask import Flask, redirect, request, url_for, session, render_template
from authlib.integrations.flask_client import OAuth
import os
import uuid
import json
import time
import requests
from openai import OpenAI

# Import the info blueprint
from info import info_bp

# Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# In-memory storage for tokens (in a real app, you'd use a database)
token_storage = {}

# OAuth setup
oauth = OAuth(app)
oauth.register(
    name='cognito',
    client_id=os.environ.get('COGNITO_CLIENT_ID'),
    client_secret=os.environ.get('COGNITO_CLIENT_SECRET'),
    server_metadata_url='https://cognito-idp.eu-west-3.amazonaws.com/eu-west-3_7lGMh3AUV/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'aws.cognito.signin.user.admin email openid phone profile https://agentapi.example.com/description https://agentapi.example.com/name'
    }
)

# Register the info blueprint
app.register_blueprint(info_bp)

# Share token_storage with the info blueprint
import info
info.token_storage = token_storage

# Start page
@app.route('/')
def index():
    return render_template('index.html')

# Login route
@app.route('/login')
def login():
    return oauth.cognito.authorize_redirect(redirect_uri='https://127.0.0.1:8888/authorize')

# Authorization callback route
@app.route('/authorize')
def authorize():
    token = oauth.cognito.authorize_access_token()
    userinfo = token.get('userinfo')
    
    # Generate a unique ID for this session
    session_id = str(uuid.uuid4())
    
    # Store token data in server-side storage
    token_storage[session_id] = {
        'token': token,
        'userinfo': userinfo
    }
    
    # Store just the session ID in the cookie
    session['auth_session_id'] = session_id
    
    # Return a success page with auto-redirect to debug
    return render_template('authorize.html')

# Debug route to display token and user information
@app.route('/debug')
def debug():
    # Get the session ID from the cookie
    session_id = session.get('auth_session_id')
    
    # Get the token data from server-side storage
    token_data = token_storage.get(session_id, {})
    token = token_data.get('token', {})
    userinfo = token_data.get('userinfo', {})
    
    # Extract groups from token or userinfo
    # Groups could be in different locations depending on the identity provider
    groups = []
    
    # Check for groups in common locations
    if 'cognito:groups' in userinfo:
        groups = userinfo['cognito:groups']
    elif 'groups' in userinfo:
        groups = userinfo['groups']
    elif 'id_token' in token and token.get('id_token_claims'):
        id_token_claims = token.get('id_token_claims', {})
        groups = id_token_claims.get('cognito:groups', id_token_claims.get('groups', []))
    
    # Store groups in a global variable for later use
    app.config['USER_GROUPS'] = groups
    
    # Format groups for display
    groups_str = json.dumps(groups, indent=2) if groups else "[]"
    
    # Convert token to a formatted string for display
    token_str = json.dumps(token, indent=2) if token else "{}"
    userinfo_str = json.dumps(userinfo, indent=2) if userinfo else "{}"
    
    return render_template('debug.html', groups_str=groups_str, token_str=token_str, userinfo_str=userinfo_str)

# Verify token route
@app.route('/verify')
def verify_token():
    # Get the session ID from the cookie
    session_id = session.get('auth_session_id')
    
    # Get the token data from server-side storage
    token_data = token_storage.get(session_id, {})
    token = token_data.get('token', {})
    
    # Extract the access token
    access_token = token.get('access_token', '')
    
    # Initialize verification results
    scopes = token.get('scope', '').split() if token.get('scope') else []
    
    # Format scopes for better display
    formatted_scopes = []
    for scope in scopes:
        if scope.startswith('https://'):
            # Extract the last part of the URL for custom scopes
            parts = scope.split('/')
            if len(parts) > 3:
                formatted_scopes.append(f"{parts[-1]} (custom)")
        else:
            formatted_scopes.append(scope)
    
    verification_results = {
        'is_valid': False,
        'token_type': token.get('token_type', ''),
        'scopes': formatted_scopes,
        'scope_count': len(scopes),
        'expires_in': token.get('expires_in', 0),
        'expiration_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + token.get('expires_in', 0))),
        'issued_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
        'error': None
    }
    
    try:
        # Simple validation - check if we have an access token
        if access_token:
            verification_results['is_valid'] = True
        else:
            verification_results['error'] = "No access token found"
    except Exception as e:
        verification_results['error'] = str(e)
    
    # Convert verification results to a formatted string for display
    verification_str = json.dumps(verification_results, indent=2)
    
    # Get the token and userinfo for display
    token_str = json.dumps(token, indent=2) if token else "{}"
    userinfo = token_data.get('userinfo', {})
    userinfo_str = json.dumps(userinfo, indent=2) if userinfo else "{}"
    
    return render_template('verify.html', 
                          verification_results=verification_results,
                          verification_str=verification_str,
                          token_str=token_str,
                          userinfo_str=userinfo_str)

# Logout route
@app.route('/logout')
def logout():
    # Clear the token from server-side storage
    session_id = session.get('auth_session_id')
    if session_id and session_id in token_storage:
        del token_storage[session_id]
    
    # Clear the session
    session.clear()
    
    cognito_logout_url = (
        "https://eu-west-37lgmh3auv.auth.eu-west-3.amazoncognito.com/logout"
        f"?client_id={os.environ.get('COGNITO_CLIENT_ID')}"
        "&logout_uri=https://127.0.0.1:8888/post_logout"
    )
    return redirect(cognito_logout_url)

# After logout Cognito redirects here
@app.route('/post_logout')
def post_logout():
    return render_template('post_logout.html')

# Generate route - only accessible to admin group
@app.route('/generate')
def generate():
    # Get the session ID from the cookie
    session_id = session.get('auth_session_id')
    
    # Get the token data from server-side storage
    token_data = token_storage.get(session_id, {})
    token = token_data.get('token', {})
    
    # Check if user is authenticated
    if not session_id or not token:
        return render_template('access_denied.html')
    
    # Get user groups from app config
    user_groups = app.config.get('USER_GROUPS', [])
    
    # Check if user is in admin group
    if 'admin' not in user_groups:
        return render_template('access_denied.html')
    
    # Get the user information
    userinfo = token_data.get('userinfo', {})
    
    # Convert userinfo to a formatted string for display
    userinfo_str = json.dumps(userinfo, indent=2) if userinfo else "{}"
    
    # Generate a joke about OAuth using OpenAI API
    client = OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Tell me a joke about OAuth !"
                    }
                ]
            }
        ],
        response_format={
            "type": "text"
        },
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        store=False
    )
    
    # Get the joke from the response
    oauth_joke = response.choices[0].message.content
    
    # User is authenticated and in admin group, render the generate template
    return render_template('generate.html', userinfo_str=userinfo_str, oauth_joke=oauth_joke)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, ssl_context='adhoc', debug=True)
