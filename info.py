from flask import Blueprint, session, render_template, current_app, redirect, url_for
import json
from openai import OpenAI

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

# Generate route - only accessible to admin group
@info_bp.route('/generate')
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
    user_groups = current_app.config.get('USER_GROUPS', [])
    
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
