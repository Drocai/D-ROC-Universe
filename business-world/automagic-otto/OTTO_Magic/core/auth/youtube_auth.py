# core/auth/youtube_auth.py - Handles YouTube API authentication
import os
import pickle
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_youtube_service(new_auth=False):
    """Authenticates and returns a YouTube service object."""
    client_secrets_file = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secrets.json")
    token_pickle_path = "token.pickle"

    if new_auth and os.path.exists(token_pickle_path):
        os.remove(token_pickle_path)

    creds = None
    if os.path.exists(token_pickle_path):
        with open(token_pickle_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"⚠️ Could not refresh token: {e}. Re-authentication is required.")
                creds = None
        if not creds:
            if not os.path.exists(client_secrets_file):
                raise FileNotFoundError(f"CRITICAL: YouTube client secrets file not found at '{client_secrets_file}'. Cannot authenticate.")
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_pickle_path, 'wb') as token:
            pickle.dump(creds, token)

    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)
