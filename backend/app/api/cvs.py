from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pypdf import PdfReader

from app import cv_store
from app.schemas.cv import CVResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/cvs", tags=["CVs"])

MAX_BYTES = 5 * 1024 * 1024


def _extract_text(filename: str, raw: bytes) -> str:
    lower = filename.lower()
    try:
        if lower.endswith(".pdf"):
            reader = PdfReader(BytesIO(raw))
            return "\n".join((page.extract_text() or "") for page in reader.pages).strip()
        if lower.endswith(".txt"):
            return raw.decode("utf-8", errors="replace").strip()
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read that file")
    raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported")


@router.post("", response_model=CVResponse, status_code=status.HTTP_201_CREATED)
def upload_cv(
    name: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    raw = file.file.read()
    if len(raw) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="File too large (max 5 MB)")
    text = _extract_text(file.filename or "", raw)
    if len(text) < 100:
        raise HTTPException(
            status_code=400,
            detail="Almost no text found. Scanned/image PDFs are not supported; use a text-based PDF",
        )
    return cv_store.create_cv(current_user["id"], name, file.filename, text)


@router.get("", response_model=list[CVResponse])
def list_my_cvs(current_user: dict = Depends(get_current_user)):
    return cv_store.list_cvs(current_user["id"])


@router.delete("/{cv_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_cv(cv_id: str, current_user: dict = Depends(get_current_user)):
    cv_store.delete_cv(current_user["id"], cv_id)