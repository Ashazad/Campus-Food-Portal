# config.py
import os

# Use env vars in prod; fall back to safe defaults for local dev
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-prod")

# Keep your SQLite file by default; can be overridden by DATABASE_URL
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///cuisine_connect.db")

# No noisy SQL logs in production
SQLALCHEMY_ECHO = False
