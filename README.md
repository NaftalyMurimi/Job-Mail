# Job Agent

An AI-powered assistant that scans your Gmail for job alerts, scores each one
against your CVs, and sends the best matches to your Telegram.

> Work in progress. Built from scratch as a learning project, ending with a
> deployment on Microsoft Azure.

## How it works

1. Connect your Gmail account
2. Upload one or more CVs
3. The app finds job-related emails (e.g. LinkedIn job alerts)
4. One OpenAI call classifies each email and scores the job against your CVs (1-10)
5. Jobs scoring above 7 are sent to you on Telegram

A later phase adds a chat assistant that helps tailor a CV to a specific job.

## Tech stack

- **Backend:** FastAPI (Python)
- **Frontend:** React + Vite
- **Database:** Supabase (PostgreSQL)
- **AI:** OpenAI API
- **Notifications:** Telegram Bot API
- **Scheduling and hosting:** Azure Functions and Azure App Service

## Project status

- [x] Phase 0: Project foundation and health check
- [ ] Phase 1: Backend core and authentication
- [ ] Phase 2: Supabase database
- [ ] Phase 3: Gmail scanner and OpenAI scoring
- [ ] Phase 4: Telegram notifications
- [ ] Phase 5: React frontend
- [ ] Phase 6: Per-user Gmail OAuth
- [ ] Phase 7: CV refinement chat
- [ ] Phase 8: Azure Functions scheduling
- [ ] Phase 9: Azure deployment and custom domain

## Running locally

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
cd ..
run_api.cmd
```

Then open http://127.0.0.1:8000/health or http://127.0.0.1:8000/docs.

## Configuration

Settings live in `backend/.env`, which is never committed. See
`backend/.env.example` for the list of variables.
