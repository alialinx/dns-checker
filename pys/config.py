import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()


MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = int(os.getenv("MONGO_PORT"))
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

MONGO_DB_USER = (os.getenv("MONGO_DB_USER") or "").strip()
MONGO_DB_PASS = (os.getenv("MONGO_DB_PASS") or "").strip()
MONGO_AUTH_SOURCE = (os.getenv("MONGO_AUTH_SOURCE") or "").strip()


MONGODB_URI = os.getenv("MONGODB_URI")

CLIENT_DAY_LIMIT = os.getenv("CLIENT_DAY_LIMIT")
CLIENT_HOUR_LIMIT = os.getenv("CLIENT_HOUR_LIMIT")
CLIENT_MINUTE_LIMIT = os.getenv("CLIENT_MINUTE_LIMIT")