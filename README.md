# OAuth Web Application Demo

This is a demonstration web application that showcases OAuth 2.0 and OpenID Connect authentication using Amazon Cognito as the identity provider.

## Features

- Secure authentication with Amazon Cognito
- OAuth 2.0 and OpenID Connect implementation
- Token verification and inspection
- Educational information about OAuth 2.0 and OpenID Connect
- Debug page to view token and user information

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Setup Instructions

### 1. Create a Python Virtual Environment

It's recommended to use a virtual environment to isolate the dependencies for this project.

#### On macOS/Linux:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

#### On Windows:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate
```

### 2. Install Required Packages

Once your virtual environment is activated, install the required packages:

```bash
pip install flask authlib requests openai
```

This will install:
- **Flask**: A lightweight web framework
- **Authlib**: Library for OAuth and OpenID Connect clients
- **Requests**: HTTP library for making API calls

### 3. Set Environment Variables

Before running the application, you need to set the following environment variables:

#### On macOS/Linux:

```bash
export COGNITO_CLIENT_ID=your_cognito_client_id
export COGNITO_CLIENT_SECRET=your_cognito_client_secret
```

#### On Windows:

```bash
set COGNITO_CLIENT_ID=your_cognito_client_id
set COGNITO_CLIENT_SECRET=your_cognito_client_secret
```

### 4. Run the Application

```bash
python app.py
```

The application will start and be available at:
- https://127.0.0.1:8888

Note: The application uses a self-signed SSL certificate for HTTPS. Your browser may show a security warning, which you can safely bypass for local development.

## Application Structure

- **app.py**: Main application file containing routes and OAuth configuration
- **info.py**: Blueprint for the OAuth educational information page
- **creds.txt**: Contains credentials for the OAuth client (not included in version control)
- **.gitignore**: Specifies files and directories that should be excluded from version control

## Usage

1. Open the application in your browser at https://127.0.0.1:8888
2. Click "Login with Cognito" to authenticate
3. After successful authentication, you'll be redirected to the debug page
4. From the debug page, you can:
   - View your token information
   - Verify your token
   - Access educational information about OAuth
   - Logout

## Security Notes

This application is for demonstration purposes only and includes several security features:

- Server-side token storage (not in cookies)
- HTTPS with SSL
- Proper OAuth 2.0 flow implementation

However, for a production environment, additional security measures would be recommended:

- Use a production-grade WSGI server
- Implement proper session management
- Store tokens in a secure database
- Use a valid SSL certificate

## License

This project is for educational purposes only.
