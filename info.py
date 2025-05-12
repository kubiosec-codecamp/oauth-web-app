from flask import Blueprint, session, render_template

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
        return render_template('access_denied.html')
    
    # Get the user information
    userinfo = token_data.get('userinfo', {})
    
    # Extract username or user identifier
    # Try different common user identifier fields
    username = userinfo.get('name', userinfo.get('preferred_username', userinfo.get('email', userinfo.get('sub', 'User'))))
    
    # User is authenticated, show the OAuth info page with welcome message
    return render_template('oauth_info.html', username=username)
