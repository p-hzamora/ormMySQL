import os
from pathlib import Path
import logging
import sys

ORMLAMBDA_DIR = Path(__file__).parent
SRC_DIR = ORMLAMBDA_DIR.parent
BASE_DIR = SRC_DIR.parent


try:
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv(str(BASE_DIR / ".env")))

except ImportError:
    print("dotenv not installed, skipping...")


GLOBAL_LOG_LEVEL = os.getenv("GLOBAL_LOG_LEVEL", "ERROR").upper()
logging.basicConfig(
    level=logging.getLevelNamesMapping().get(GLOBAL_LOG_LEVEL, logging.ERROR),
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(BASE_DIR / "errors.log"), "w", encoding="utf-8"),
    ],
)

log = logging.getLogger(__name__)
log.info(f"GLOBAL_LOG_LEVEL: {GLOBAL_LOG_LEVEL}")
