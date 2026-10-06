import base64
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BACKEND_DIR = Path(__file__).resolve().parents[2]
TOKEN_PATH = BACKEND_DIR / "token.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailAuthError(Exception):
    pass


def get_gmail_service():
    if not TOKEN_PATH.exists():
        raise GmailAuthError("token.json not found. Run: python scripts\\gmail_auth.py")
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    try:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
    except RefreshError:
        raise GmailAuthError("Gmail login expired. Re-run: python scripts\\gmail_auth.py")
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def list_message_ids(service, query: str, max_results: int) -> list[str]:
    resp = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    return [m["id"] for m in resp.get("messages", [])]


def _decode(data: str) -> str:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode("utf-8", errors="replace")


def _walk(part: dict, plain: list, html: list) -> None:
    mime = part.get("mimeType", "")
    data = part.get("body", {}).get("data")
    if data:
        if mime == "text/plain":
            plain.append(_decode(data))
        elif mime == "text/html":
            html.append(_decode(data))
    for sub in part.get("parts") or []:
        _walk(sub, plain, html)


def _extract_body(payload: dict) -> str:
    plain, html = [], []
    _walk(payload, plain, html)
    if plain:
        text = "\n".join(plain)
    elif html:
        text = BeautifulSoup("\n".join(html), "html.parser").get_text(separator="\n")
    else:
        text = ""
    lines = (line.strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line)


def get_message(service, msg_id: str) -> dict:
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
    received = datetime.fromtimestamp(int(msg["internalDate"]) / 1000, tz=timezone.utc).isoformat()
    return {
        "id": msg_id,
        "subject": headers.get("subject", "(no subject)"),
        "sender": headers.get("from", ""),
        "received_at": received,
        "body": _extract_body(msg["payload"]),
    }