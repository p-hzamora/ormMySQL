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

DB_USERNAME = os.getenv("USERNAME", 'root')

DB_PASSWORD = os.getenv("PASSWORD", 'root')

DB_HOST = os.getenv("HOST", "localhost")

DB_DATABASE = os.getenv("DATABASE", "sakila")
