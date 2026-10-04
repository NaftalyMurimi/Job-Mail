import sys
from loguru import logger


def setup_logger(debug: bool):
    # Remove loguru's default handler so we control the format and level
    logger.remove()

    # Console output: verbose when debugging, quieter otherwise
    logger.add(sys.stderr, level="DEBUG" if debug else "INFO")

    # File output: rotates at 5 MB, keeps one week of history
    logger.add("logs/app.log", rotation="5 MB", retention="7 days", level="INFO")


# Re-exported so other files can do: from app.utils.logger import logger
__all__ = ["logger", "setup_logger"]