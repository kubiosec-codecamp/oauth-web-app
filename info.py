from flask import Blueprint, session

# Import token_storage from the main app
# This will be set when we register the blueprint
token_storage = None

# Create a Blueprint for the info routes
info_bp = Blueprint('info', __name__)

# OAuth Info route
@info_bp.route('/info')
def oauth_info():
    # Get the session ID from the cookie
    session_id = session.get('auth_session_id')
    
    # Get the token data from server-side storage
    token_data = token_storage.get(session_id, {})
    token = token_data.get('token', {})
    
    # Check if user is authenticated
    if not session_id or not token:
        return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Access Denied - OAuth Demo App</title>
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
                    margin-bottom: 2rem;
                    text-align: center;
                    padding: 2rem;
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
                .access-icon {
                    font-size: 3rem;
                    color: #dc3545;
                    margin-bottom: 1rem;
                }
                .access-header {
                    color: #dc3545;
                    margin-bottom: 1.5rem;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-lg-6">
                        <div class="card">
                            <div class="access-icon">
                                <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="currentColor" class="bi bi-shield-lock" viewBox="0 0 16 16">
                                    <path d="M5.338 1.59a61.44 61.44 0 0 0-2.837.856.481.481 0 0 0-.328.39c-.554 4.157.726 7.19 2.253 9.188a10.725 10.725 0 0 0 2.287 2.233c.346.244.652.42.893.533.12.057.218.095.293.118a.55.55 0 0 0 .101.025.615.615 0 0 0 .1-.025c.076-.023.174-.061.294-.118.24-.113.547-.29.893-.533a10.726 10.726 0 0 0 2.287-2.233c1.527-1.997 2.807-5.031 2.253-9.188a.48.48 0 0 0-.328-.39c-.651-.213-1.75-.56-2.837-.855C9.552 1.29 8.531 1.067 8 1.067c-.53 0-1.552.223-2.662.524zM5.072.56C6.157.265 7.31 0 8 0s1.843.265 2.928.56c1.11.3 2.229.655 2.887.87a1.54 1.54 0 0 1 1.044 1.262c.596 4.477-.787 7.795-2.465 9.99a11.775 11.775 0 0 1-2.517 2.453 7.159 7.159 0 0 1-1.048.625c-.28.132-.581.24-.829.24s-.548-.108-.829-.24a7.158 7.158 0 0 1-1.048-.625 11.777 11.777 0 0 1-2.517-2.453C1.928 10.487.545 7.169 1.141 2.692A1.54 1.54 0 0 1 2.185 1.43 62.456 62.456 0 0 1 5.072.56z"/>
                                    <path d="M9.5 6.5a1.5 1.5 0 0 1-1 1.415l.385 1.99a.5.5 0 0 1-.491.595h-.788a.5.5 0 0 1-.49-.595l.384-1.99a1.5 1.5 0 1 1 2-1.415z"/>
                                </svg>
                            </div>
                            <h1 class="access-header">No Access</h1>
                            <p class="lead mb-4">Please login to view this page.</p>
                            <a href="/" class="btn btn-primary">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-house-door me-2" viewBox="0 0 16 16">
                                    <path d="M8.354 1.146a.5.5 0 0 0-.708 0l-6 6A.5.5 0 0 0 1.5 7.5v7a.5.5 0 0 0 .5.5h4.5a.5.5 0 0 0 .5-.5v-4h2v4a.5.5 0 0 0 .5.5H14a.5.5 0 0 0 .5-.5v-7a.5.5 0 0 0-.146-.354L13 5.793V2.5a.5.5 0 0 0-.5-.5h-1a.5.5 0 0 0-.5.5v1.293L8.354 1.146zM2.5 14V7.707l5.5-5.5 5.5 5.5V14H10v-4a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5v4H2.5z"/>
                                </svg>
                                Go to Home
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        '''
    
    # Get the user information
    userinfo = token_data.get('userinfo', {})
    
    # Extract username or user identifier
    # Try different common user identifier fields
    username = userinfo.get('name', userinfo.get('preferred_username', userinfo.get('email', userinfo.get('sub', 'User'))))
    
    # User is authenticated, show the OAuth info page with welcome message
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OAuth Information - OAuth Demo App</title>
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
            .info-header {{
                color: #6e8efb;
                margin-bottom: 2rem;
                text-align: center;
            }}
            .info-text {{
                line-height: 1.7;
            }}
            .flow-diagram {{
                max-width: 100%;
                height: auto;
                margin: 2rem 0;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <h1 class="info-header">Understanding OAuth 2.0</h1>
                    <div class="alert alert-success text-center mb-4">
                        <h5 class="mb-0">Welcome, {username}!</h5>
                    </div>
                    <div class="d-flex justify-content-center mb-4">
                        <a href="/debug" class="btn btn-outline-primary">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-left me-2" viewBox="0 0 16 16">
                                <path fill-rule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8z"/>
                            </svg>
                            Return to Debug
                        </a>
                    </div>
                    
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">What is OAuth 2.0?</h5>
                        </div>
                        <div class="card-body">
                            <div class="info-text">
                                <p>OAuth 2.0 is an authorization framework that enables a third-party application to obtain limited access to a service on behalf of a user. It works by delegating user authentication to the service that hosts the user account and authorizing third-party applications to access that user account.</p>
                                
                                <p>OAuth 2.0 provides a secure way for users to grant applications access to their information without sharing their credentials (username and password) with those applications.</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">Key OAuth 2.0 Concepts</h5>
                        </div>
                        <div class="card-body">
                            <div class="info-text">
                                <h6>Roles in OAuth 2.0:</h6>
                                <ul>
                                    <li><strong>Resource Owner:</strong> The user who owns the data (you)</li>
                                    <li><strong>Client:</strong> The application requesting access to the user's data</li>
                                    <li><strong>Authorization Server:</strong> The server that authenticates the user and issues tokens</li>
                                    <li><strong>Resource Server:</strong> The server hosting the protected resources</li>
                                </ul>
                                
                                <h6>Types of Tokens:</h6>
                                <ul>
                                    <li><strong>Access Token:</strong> A credential used to access protected resources</li>
                                    <li><strong>Refresh Token:</strong> A credential used to obtain new access tokens when they expire</li>
                                    <li><strong>ID Token:</strong> Contains claims about the authentication of an end-user (used in OpenID Connect)</li>
                                </ul>
                                
                                <h6>Grant Types:</h6>
                                <ul>
                                    <li><strong>Authorization Code:</strong> Used by web and mobile apps, most secure flow</li>
                                    <li><strong>Implicit:</strong> Simplified flow for browser-based applications (less secure)</li>
                                    <li><strong>Resource Owner Password Credentials:</strong> Direct username/password authentication</li>
                                    <li><strong>Client Credentials:</strong> Used for machine-to-machine communication</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">OAuth 2.0 Flow (Authorization Code Grant)</h5>
                        </div>
                        <div class="card-body">
                            <div class="info-text">
                                <ol>
                                    <li><strong>Authorization Request:</strong> The client redirects the user to the authorization server</li>
                                    <li><strong>User Authentication:</strong> The user logs in and grants permissions</li>
                                    <li><strong>Authorization Code:</strong> The authorization server redirects back to the client with an authorization code</li>
                                    <li><strong>Token Request:</strong> The client exchanges the authorization code for an access token</li>
                                    <li><strong>Token Response:</strong> The authorization server issues an access token (and optionally a refresh token)</li>
                                    <li><strong>Resource Access:</strong> The client uses the access token to access protected resources</li>
                                </ol>
                                
                                <div class="text-center">
                                    <img src="https://www.oauth.com/wp-content/uploads/2018/05/oauth-2-flow-diagram.png" alt="OAuth 2.0 Flow Diagram" class="flow-diagram">
                                    <p class="text-muted small">Image source: oauth.com</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">Security Considerations</h5>
                        </div>
                        <div class="card-body">
                            <div class="info-text">
                                <ul>
                                    <li><strong>Always use HTTPS</strong> for all OAuth 2.0 communications</li>
                                    <li><strong>Validate all tokens</strong> and their claims before trusting them</li>
                                    <li><strong>Use PKCE (Proof Key for Code Exchange)</strong> for public clients to prevent authorization code interception</li>
                                    <li><strong>Implement proper token storage</strong> and avoid storing tokens in local storage</li>
                                    <li><strong>Set appropriate token expiration times</strong> to limit the damage if tokens are compromised</li>
                                    <li><strong>Validate redirect URIs</strong> to prevent open redirector attacks</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">OpenID Connect</h5>
                        </div>
                        <div class="card-body">
                            <div class="info-text">
                                <p>OpenID Connect (OIDC) is an identity layer built on top of OAuth 2.0. While OAuth 2.0 is focused on authorization (granting access), OIDC adds authentication (verifying identity).</p>
                                
                                <p>OIDC introduces the ID Token, which is a JWT (JSON Web Token) containing claims about the authentication event and the user's identity. This allows applications to verify the user's identity and obtain basic profile information.</p>
                                
                                <p>Amazon Cognito, which is used in this demo application, supports both OAuth 2.0 and OpenID Connect protocols.</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="d-flex justify-content-center mt-4">
                        <a href="/debug" class="btn btn-outline-primary">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-left me-2" viewBox="0 0 16 16">
                                <path fill-rule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8z"/>
                            </svg>
                            Return to Debug
                        </a>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''
