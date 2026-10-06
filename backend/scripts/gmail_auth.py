from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

BACKEND_DIR = Path(__file__).resolve().parents[1]
CREDENTIALS = BACKEND_DIR / "credentials.json"
TOKEN = BACKEND_DIR / "token.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS), SCOPES)
creds = flow.run_local_server(port=0, prompt="consent")
TOKEN.write_text(creds.to_json())
print(f"Saved {TOKEN}")