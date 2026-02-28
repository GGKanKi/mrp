import os
from google.oauth2 import service_account
from dotenv import load_dotenv
from pathlib import Path

API_KEY = os.getenv("API_KEY")

#Pathing
BASE_DIR = Path(__file__).resolve().parent

# Load your paths from .env
load_dotenv()
CRED_PATH = os.path.join(BASE_DIR, "json_f", "new_cred.json")
TOKEN_PATH = os.path.join(BASE_DIR, "json_f", "token.json")

# SHEETS LINK
USER_LOG = os.getenv('USERLOG')
ACTION_LOG = os.getenv('ACTION_LOG')
PRODUCT_LOG = os.getenv('PRODUCT_LOG')
SETTING_LOG = os.getenv('SETTING_LOG')
RESTOCK_LOG = os.getenv('RESTOCK_LOG')