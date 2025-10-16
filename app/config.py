import os
from dotenv import load_dotenv

load_dotenv()

APP_TITLE = os.getenv("APP_TITLE", "Multi-Tab Dashboard")
APP_ICON = os.getenv("APP_ICON", "")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False") == "True"
