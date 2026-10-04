from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.utils.logger import logger, setup_logger

# Configure logging before anything else runs
setup_logger(settings.debug)

app = FastAPI(title=settings.app_name)

# CORS lets the React dev server (Vite, port 5173) call this API.
# Both hostnames are listed because browsers treat them as different origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    # Simple endpoint to confirm the server is up
    logger.info("Health check called")
    return {"status": "ok", "app": settings.app_name}