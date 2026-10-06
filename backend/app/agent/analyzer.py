import json

from openai import OpenAI

from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)

MAX_EMAIL_CHARS = 4000
MAX_CV_CHARS = 6000

RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "is_job_advert": {"type": "boolean"},
        "category": {"type": "string"},
        "job_title": {"type": ["string", "null"]},
        "company": {"type": ["string", "null"]},
        "match_score": {"type": ["integer", "null"]},
        "best_cv_number": {"type": ["integer", "null"]},
        "reasoning": {"type": "string"},
    },
    "required": [
        "is_job_advert", "category", "job_title", "company",
        "match_score", "best_cv_number", "reasoning",
    ],
    "additionalProperties": False,
}

SYSTEM_PROMPT = """You are a job-search assistant. You receive one email and the candidate's CVs.

1. Decide whether the email advertises or lists one or more specific job openings
   (job alerts, job digests, recruiter outreach about a role). Newsletters, marketing,
   application receipts, rejections and general notifications are NOT job adverts.
2. If it is a job advert and lists several jobs, evaluate only the single best-matching job.
3. Compare that job against EVERY CV. Choose the CV that fits best (best_cv_number) and give
   match_score from 1 (no fit) to 10 (excellent fit), judging skills, experience and seniority.
   Be strict: 9-10 only when the CV clearly satisfies the main requirements.
4. category: a short snake_case label such as ai_ml, data_analysis, software_dev, other_job, not_job.
5. reasoning: two sentences max, naming the strongest match and the biggest gap.
6. If it is not a job advert, set job_title, company, match_score and best_cv_number to null."""


def analyze_email(email: dict, cvs: list[dict]) -> dict:
    cv_block = "\n\n".join(
        f"=== CV {i} ({cv['name']}) ===\n{cv['content_text'][:MAX_CV_CHARS]}"
        for i, cv in enumerate(cvs, start=1)
    )
    user_prompt = (
        f"CANDIDATE CVS:\n{cv_block}\n\n"
        f"EMAIL\nFrom: {email['sender']}\nSubject: {email['subject']}\n\n"
        f"{email['body'][:MAX_EMAIL_CHARS]}"
    )

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "email_analysis", "strict": True, "schema": RESULT_SCHEMA},
        },
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("OpenAI returned no content")
    return _clean(json.loads(content), cvs)


def _clean(data: dict, cvs: list[dict]) -> dict:
    is_job = bool(data["is_job_advert"])
    score, cv_id = None, None
    if is_job:
        if isinstance(data["match_score"], int):
            score = max(1, min(10, data["match_score"]))
        n = data["best_cv_number"]
        if isinstance(n, int) and 1 <= n <= len(cvs):
            cv_id = cvs[n - 1]["id"]
    return {
        "is_job_advert": is_job,
        "category": data["category"],
        "job_title": data["job_title"] if is_job else None,
        "company": data["company"] if is_job else None,
        "match_score": score,
        "best_matching_cv_id": cv_id,
        "reasoning": data["reasoning"],
    }