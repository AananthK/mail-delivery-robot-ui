import os
import psycopg2
from psycopg2.extras import RealDictCursor

from dotenv import load_dotenv

#load variables from dotenv into environment
load_dotenv()

USE_SUPABASE = os.getenv("USE_SUPABASE", "false").lower() == "true"

if USE_SUPABASE:
    DB_URL = os.getenv("SUPABASE_URL")
else:
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT]):
        raise ValueError("Database environment variables are not set correctly.")

def get_connection():

    if USE_SUPABASE:
        conn = psycopg2.connect(
            DB_URL,
            cursor_factory=RealDictCursor, # all cursors return dicts
            sslmode="require"
        )
    else:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            cursor_factory=RealDictCursor # all cursors return dicts
            # no sslmode here
        )

    return conn
