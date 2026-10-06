from fastapi import APIRouter, Depends, HTTPException, Query

from app import email_store
from app.agent.gmail_client import GmailAuthError
from app.agent.scanner import NoCVsError, run_scan
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/scan", tags=["Scan"])


@router.post("")
def trigger_scan(
    max_emails: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
):
    try:
        return run_scan(current_user["id"], max_emails)
    except NoCVsError:
        raise HTTPException(status_code=400, detail="Upload at least one CV first (POST /cvs)")
    except GmailAuthError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/results")
def scan_results(
    min_score: int | None = Query(None, ge=1, le=10),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
):
    return email_store.list_scanned(current_user["id"], min_score, limit)