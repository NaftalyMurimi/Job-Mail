from loguru import logger

from app import cv_store, email_store
from app.agent.analyzer import analyze_email
from app.agent.gmail_client import get_gmail_service, get_message, list_message_ids
from app.config import settings


class NoCVsError(Exception):
    pass


def run_scan(user_id: str, max_emails: int = 10) -> dict:
    cvs = cv_store.get_cvs_with_text(user_id)
    if not cvs:
        raise NoCVsError("No CVs uploaded")

    service = get_gmail_service()
    ids = list_message_ids(service, settings.gmail_query, max_emails)
    existing = email_store.get_existing_message_ids(user_id, ids)
    new_ids = [i for i in ids if i not in existing]

    summary = {
        "fetched": len(ids),
        "already_scanned": len(existing),
        "analyzed": 0,
        "job_adverts": 0,
        "above_threshold": 0,
        "errors": 0,
    }
    logger.info(f"Scan started: {len(new_ids)} new emails to analyze")

    for msg_id in new_ids:
        try:
            email = get_message(service, msg_id)
            analysis = analyze_email(email, cvs)
            email_store.save_scanned_email(user_id, email, analysis)
        except Exception:
            logger.exception(f"Failed to process email {msg_id}")
            summary["errors"] += 1
            continue

        summary["analyzed"] += 1
        if analysis["is_job_advert"]:
            summary["job_adverts"] += 1
            score = analysis["match_score"] or 0
            logger.info(f"JOB score={score} | {analysis['job_title']} @ {analysis['company']}")
            if score > settings.notify_threshold:
                summary["above_threshold"] += 1

    logger.info(f"Scan finished: {summary}")
    return summary