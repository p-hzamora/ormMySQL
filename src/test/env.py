from pathlib import Path
import os

APP_DIR = Path(__file__).parent
TEST_DIR = APP_DIR.parent
SRC_DIR = TEST_DIR.parent
BASE_DIR = SRC_DIR.parent

try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv(str(BASE_DIR / ".env")))

except ImportError:
    print("python-dotenv is not installed. Skipping...")


#################################
# Load DATABASE ENV
#################################

DB_PREFIX = os.getenv("DB_PREFIX","mysql://")

DB_USERNAME = os.getenv("USERNAME", "root")

DB_PASSWORD = os.getenv("PASSWORD", "root")

DB_HOST = os.getenv("DB_HOST", "localhost")

DB_PORT = os.getenv("DB_PORT", "3306")

DB_DATABASE = os.getenv("DATABASE", "sakila")

# dialect+driver://username:password@host:port/database
DATABASE_URL = os.getenv("DATABASE_URL",None)

if DATABASE_URL is None:
    DATABASE_URL = f"{DB_PREFIX}{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
