import psycopg2
from dotenv import load_dotenv
import os
from urllib.parse import urlparse

# Load environment variables from .env
load_dotenv()

# Try to get the connection URL (Pooler or Direct)
DATABASE_URL = os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")

if DATABASE_URL:
    print(f"Parsing connection string: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else '...'}")
    result = urlparse(DATABASE_URL)
    USER = result.username
    PASSWORD = result.password
    HOST = result.hostname
    PORT = result.port
    DBNAME = result.path[1:] # remove leading slash
else:
    # Fallback to individual vars
    USER = os.getenv("POSTGRES_USER")
    PASSWORD = os.getenv("POSTGRES_PASSWORD")
    HOST = os.getenv("POSTGRES_HOST")
    DBNAME = os.getenv("POSTGRES_DATABASE")
    PORT = os.getenv("PORT", "5432")

print(f"Connecting to {HOST}:{PORT} as {USER}...")

# Connect to the database
try:
    with psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    ) as connection:
        print("Connection successful!")

        # Create a cursor to execute SQL queries
        with connection.cursor() as cursor:
            # Example query
            cursor.execute("SELECT NOW();")
            result = cursor.fetchone()
            print("Current Time:", result)

        print("Connection closed.")

except psycopg2.Error as e:
    print(f"Failed to connect: {e}")
