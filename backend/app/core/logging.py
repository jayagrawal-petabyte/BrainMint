import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    root = logging.getLogger()
    if getattr(root, "_brainmint_configured", False):
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)-8s [%(name)s] %(message)s")
    )
    root.handlers = [handler]
    root.setLevel(settings.LOG_LEVEL.upper())
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    root._brainmint_configured = True  # type: ignore[attr-defined]