import logging
import sys

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    level = logging.DEBUG if settings.app_env == "development" else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        stream=sys.stdout,
    )
    logging.getLogger("app").info("Logging configured (app_env=%s)", settings.app_env)
