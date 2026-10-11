import json

from openai import OpenAI

from app.config import settings

# Works with any OpenAI-compatible provider (Groq now, OpenAI later): only .env changes.
# max_retries makes the SDK wait and retry automatically when a rate limit (429) is hit.
client = OpenAI(
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
    max_retries=6,
)

MAX_EMAIL_CHARS = 4000
MAX_CV_CHARS = 6000

SYSTEM_PROMPT = """You are a job-search assistant. You receive one email and the candidate's CVs.

1. Decide whether the email advertises or lists one or more specific job openings
   (job alerts, job digests, recruiter outreach about a role). Newsletters, marketing,
   application receipts, rejections and general notifications are NOT job adverts.
2. If it is a job advert and lists several jobs, evaluate only the single best-matching job.
3. Compare that job against EVERY CV. Choose the CV that fits best (best_cv_number) and give
   match_score from 1 (no fit) to 10 (excellent fit), judging skills, experience and seniority.
   Be strict: 9-10 only when the CV clearly satisfies the main requirements.
4. If it is not a job advert, set job_title, company, match_score and best_cv_number to null.

Respond with ONLY a JSON object with exactly these keys:
{
  "is_job_advert": true or false,
  "category": "short_snake_case_label such as ai_ml, data_analysis, software_dev, other_job, not_job",
  "job_title": "string or null",
  "company": "string or null",
  "match_score": integer from 1 to 10, or null,
  "best_cv_number": integer (the CV number as labelled below), or null,
  "reasoning": "two sentences max: strongest match and biggest gap"
}"""


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
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("The model returned no content")
    return _clean(json.loads(content), cvs)


def _clean(data: dict, cvs: list[dict]) -> dict:
    """Never trust model output: validate every field before it reaches the database."""
    is_job = data.get("is_job_advert") is True
    score, cv_id = None, None
    if is_job:
        raw_score = data.get("match_score")
        if isinstance(raw_score, (int, float)):
            score = max(1, min(10, int(raw_score)))
        n = data.get("best_cv_number")
        if isinstance(n, int) and 1 <= n <= len(cvs):
            cv_id = cvs[n - 1]["id"]
    return {
        "is_job_advert": is_job,
        "category": str(data.get("category") or ("other_job" if is_job else "not_job")),
        "job_title": data.get("job_title") if is_job else None,
        "company": data.get("company") if is_job else None,
        "match_score": score,
        "best_matching_cv_id": cv_id,
        "reasoning": str(data.get("reasoning") or ""),
    }