from flask import Flask, redirect, request, url_for, session
from authlib.integrations.flask_client import OAuth
import os
import uuid
import json
import time
import requests

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
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OAuth Demo App</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .hero {
                height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, #6e8efb, #a777e3);
                color: white;
            }
            .card {
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                border: none;
                padding: 2rem;
                background: white;
                color: #6e8efb;
                max-width: 800px; /* Increased width */
                margin: 0 auto; /* Center the card */
            }
            .btn-primary {
                background: linear-gradient(135deg, #6e8efb, #a777e3);
                border: none;
                padding: 10px 25px;
                border-radius: 50px;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .btn-primary:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            }
        </style>
    </head>
    <body>
        <div class="hero">
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-md-8"> <!-- Adjusted column width -->
                        <div class="card text-center">
                            <div class="card-body">
                                <h1 class="display-4 mb-4">Welcome to #hacktolearn by xxradar</h1>
                                <p class="lead mb-4">This is a secure OAuth authentication demo application.</p>
                                <a href="/login" class="btn btn-primary btn-lg">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-shield-lock me-2" viewBox="0 0 16 16">
                                        <path d="M5.338 1.59a61.44 61.44 0 0 0-2.837.856.481.481 0 0 0-.328.39c-.554 4.157.726 7.19 2.253 9.188a10.725 10.725 0 0 0 2.287 2.233c.346.244.652.42.893.533.12.057.218.095.293.118a.55.55 0 0 0 .101.025.615.615 0 0 0 .1-.025c.076-.023.174-.061.294-.118.24-.113.547-.29.893-.533a10.726 10.726 0 0 0 2.287-2.233c1.527-1.997 2.807-5.031 2.253-9.188a.48.48 0 0 0-.328-.39c-.651-.213-1.75-.56-2.837-.855C9.552 1.29 8.531 1.067 8 1.067c-.53 0-1.552.223-2.662.524zM5.072.56C6.157.265 7.31 0 8 0s1.843.265 2.928.56c1.11.3 2.229.655 2.887.87a1.54 1.54 0 0 1 1.044 1.262c.596 4.477-.787 7.795-2.465 9.99a11.775 11.775 0 0 1-2.517 2.453 7.159 7.159 0 0 1-1.048.625c-.28.132-.581.24-.829.24s-.548-.108-.829-.24a7.158 7.158 0 0 1-1.048-.625 11.777 11.777 0 0 1-2.517-2.453C1.928 10.487.545 7.169 1.141 2.692A1.54 1.54 0 0 1 2.185 1.43 62.456 62.456 0 0 1 5.072.56z"/>
                                        <path d="M9.5 6.5a1.5 1.5 0 0 1-1 1.415l.385 1.99a.5.5 0 0 1-.491.595h-.788a.5.5 0 0 1-.49-.595l.384-1.99a1.5 1.5 0 1 1 2-1.415z"/>
                                    </svg>
                                    Login with Cognito
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''

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
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login Success - OAuth Demo App</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                padding-top: 2rem;
                padding-bottom: 2rem;
            }
            .card {
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                border: none;
                padding: 2rem;
                background: white;
                color: #6e8efb;
                text-align: center;
            }
            .success-icon {
                font-size: 3rem;
                color: #6e8efb;
                margin-bottom: 1rem;
            }
        </style>
        <meta http-equiv="refresh" content="1;url=/debug" />
    </head>
    <body>
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="success-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="currentColor" class="bi bi-check-circle-fill" viewBox="0 0 16 16">
                                <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
                            </svg>
                        </div>
                        <h1 class="display-4 mb-3">Login Successful!</h1>
                        <p class="lead mb-4">You have been successfully authenticated with Cognito.</p>
                        <div class="d-flex justify-content-center">
                            <div class="spinner-border text-primary me-2" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <p class="mb-0 text-primary">Redirecting to debug page...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''

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
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Debug Info - OAuth Demo App</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                padding-top: 2rem;
                padding-bottom: 2rem;
            }}
            .card {{
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                border: none;
                margin-bottom: 2rem;
            }}
            .card-header {{
                background: linear-gradient(135deg, #6e8efb, #a777e3);
                color: white;
                border-radius: 15px 15px 0 0 !important;
                padding: 1rem 1.5rem;
                font-weight: 600;
            }}
            pre {{
                background-color: #f8f9fa;
                padding: 1rem;
                border-radius: 10px;
                max-height: 300px;
                overflow-y: auto;
            }}
            .btn-outline-primary {{
                color: #6e8efb;
                border-color: #6e8efb;
                border-radius: 50px;
                padding: 10px 25px;
                font-weight: 600;
                transition: all 0.3s ease;
            }}
            .btn-outline-primary:hover {{
                background-color: #6e8efb;
                color: white;
                transform: translateY(-3px);
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            }}
            .debug-header {{
                color: #6e8efb;
                margin-bottom: 2rem;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <h1 class="debug-header">OAuth Debug Information</h1>
                    
                    <div class="d-flex justify-content-center mb-4">
                        <a href="/verify" class="btn btn-outline-primary me-2">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-circle me-2" viewBox="0 0 16 16">
                                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                                <path d="M10.97 4.97a.235.235 0 0 0-.02.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-1.071-1.05z"/>
                            </svg>
                            Verify Token
                        </a>
                        <a href="/info" class="btn btn-outline-primary me-2">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-info-circle me-2" viewBox="0 0 16 16">
                                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                                <path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/>
                            </svg>
                            OAuth Info
                        </a>
                        <a href="/logout" class="btn btn-outline-primary">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-box-arrow-right me-2" viewBox="0 0 16 16">
                                <path fill-rule="evenodd" d="M10 12.5a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v2a.5.5 0 0 0 1 0v-2A1.5 1.5 0 0 0 9.5 2h-8A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-2a.5.5 0 0 0-1 0v2z"/>
                                <path fill-rule="evenodd" d="M15.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L14.293 7.5H5.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z"/>
                            </svg>
                            Logout
                        </a>
                    </div>
                    
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">User Groups</h5>
                        </div>
                        <div class="card-body">
                            <pre class="mb-0">{groups_str}</pre>
                        </div>
                    </div>
                    
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">Token Information</h5>
                        </div>
                        <div class="card-body">
                            <pre class="mb-0">{token_str}</pre>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">User Information</h5>
                        </div>
                        <div class="card-body">
                            <pre class="mb-0">{userinfo_str}</pre>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''

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
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Token Verification - OAuth Demo App</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                padding-top: 2rem;
                padding-bottom: 2rem;
            }}
            .card {{
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                border: none;
                margin-bottom: 2rem;
            }}
            .card-header {{
                background: linear-gradient(135deg, #6e8efb, #a777e3);
                color: white;
                border-radius: 15px 15px 0 0 !important;
                padding: 1rem 1.5rem;
                font-weight: 600;
            }}
            pre {{
                background-color: #f8f9fa;
                padding: 1rem;
                border-radius: 10px;
                max-height: 300px;
                overflow-y: auto;
            }}
            .btn-outline-primary {{
                color: #6e8efb;
                border-color: #6e8efb;
                border-radius: 50px;
                padding: 10px 25px;
                font-weight: 600;
                transition: all 0.3s ease;
                margin: 0 5px;
            }}
            .btn-outline-primary:hover {{
                background-color: #6e8efb;
                color: white;
                transform: translateY(-3px);
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            }}
            .debug-header {{
                color: #6e8efb;
                margin-bottom: 2rem;
                text-align: center;
            }}
            .valid-badge {{
                background-color: #28a745;
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 50px;
                font-weight: 600;
                display: inline-block;
                margin-left: 1rem;
            }}
            .invalid-badge {{
                background-color: #dc3545;
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 50px;
                font-weight: 600;
                display: inline-block;
                margin-left: 1rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <h1 class="debug-header">
                        Token Verification
                        <span class="{verification_results['is_valid'] and 'valid-badge' or 'invalid-badge'}">
                            {verification_results['is_valid'] and 'Valid' or 'Invalid'}
                        </span>
                    </h1>
                    
                    <div class="d-flex justify-content-center mb-4">
                        <a href="/debug" class="btn btn-outline-primary">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-left me-2" viewBox="0 0 16 16">
                                <path fill-rule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8z"/>
                            </svg>
                            Back to Debug
                        </a>
                        <a href="/logout" class="btn btn-outline-primary">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-box-arrow-right me-2" viewBox="0 0 16 16">
                                <path fill-rule="evenodd" d="M10 12.5a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v2a.5.5 0 0 0 1 0v-2A1.5 1.5 0 0 0 9.5 2h-8A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-2a.5.5 0 0 0-1 0v2z"/>
                                <path fill-rule="evenodd" d="M15.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L14.293 7.5H5.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z"/>
                            </svg>
                            Logout
                        </a>
                    </div>
                    
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">Verification Results</h5>
                        </div>
                        <div class="card-body">
                            <pre class="mb-0">{verification_str}</pre>
                        </div>
                    </div>
                    
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">Token Information</h5>
                        </div>
                        <div class="card-body">
                            <pre class="mb-0">{token_str}</pre>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">User Information</h5>
                        </div>
                        <div class="card-body">
                            <pre class="mb-0">{userinfo_str}</pre>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''

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
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Logged Out - OAuth Demo App</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .logout-container {
                height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .card {
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                border: none;
                padding: 2rem;
                text-align: center;
                background: white;
                color: #6e8efb;
            }
            .btn-primary {
                background: linear-gradient(135deg, #6e8efb, #a777e3);
                border: none;
                padding: 10px 25px;
                border-radius: 50px;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .btn-primary:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            }
        </style>
    </head>
    <body>
        <div class="logout-container">
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-md-6">
                        <div class="card">
                            <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="#6e8efb" class="bi bi-box-arrow-right mb-4" viewBox="0 0 16 16">
                                <path fill-rule="evenodd" d="M10 12.5a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v2a.5.5 0 0 0 1 0v-2A1.5 1.5 0 0 0 9.5 2h-8A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-2a.5.5 0 0 0-1 0v2z"/>
                                <path fill-rule="evenodd" d="M15.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L14.293 7.5H5.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z"/>
                            </svg>
                            <h1 class="display-4 mb-3">Logged Out</h1>
                            <p class="lead mb-4">You have been successfully logged out of the OAuth Demo App.</p>
                            <a href="/" class="btn btn-primary">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-house-door me-2" viewBox="0 0 16 16">
                                    <path d="M8.354 1.146a.5.5 0 0 0-.708 0l-6 6A.5.5 0 0 0 1.5 7.5v7a.5.5 0 0 0 .5.5h4.5a.5.5 0 0 0 .5-.5v-4h2v4a.5.5 0 0 0 .5.5H14a.5.5 0 0 0 .5-.5v-7a.5.5 0 0 0-.146-.354L13 5.793V2.5a.5.5 0 0 0-.5-.5h-1a.5.5 0 0 0-.5.5v1.293L8.354 1.146zM2.5 14V7.707l5.5-5.5 5.5 5.5V14H10v-4a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5v4H2.5z"/>
                                </svg>
                                Return to Home
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, ssl_context='adhoc', debug=True)
