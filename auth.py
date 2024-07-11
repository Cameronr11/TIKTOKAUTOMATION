import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import google.auth.transport.requests
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Define the absolute path to the client_secret.json file
project_dir = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.join(project_dir, "client_secret.json")
print("Client secrets file path:", CLIENT_SECRETS_FILE)
print("Directory contents:", os.listdir(project_dir))

def get_authenticated_service():
    credentials = None
    token_file = os.path.join(project_dir, 'token.json')

    if os.path.exists(token_file):
        credentials = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(google.auth.transport.requests.Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            flow.redirect_uri = 'http://localhost:8081/'
            credentials = flow.run_local_server(port=8081)
        with open(token_file, 'w') as token:
            token.write(credentials.to_json())

    return googleapiclient.discovery.build(
        "youtube", "v3", credentials=credentials)


