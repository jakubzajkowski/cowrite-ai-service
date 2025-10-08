#!/usr/bin/env python3
"""
Wait for database to be ready before running migrations.
"""
import sys
import time
import os
from urllib.parse import urlparse, unquote
import psycopg2
from psycopg2 import OperationalError


def parse_database_url(url: str) -> dict:
    """Parse database URL into connection parameters safely."""
    # Remove SQLAlchemy driver prefix if present
    if "://" not in url:
        raise ValueError(f"Invalid database URL: {url}")
    scheme, rest = url.split("://", 1)
    if "+" in scheme:
        scheme = scheme.split("+")[0]
    parsed = urlparse(f"{scheme}://{rest}")

    # Decode URL-encoded username and password
    username = unquote(parsed.username) if parsed.username else None
    password = unquote(parsed.password) if parsed.password else None

    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 5432,
        "user": username,
        "password": password,
        "database": parsed.path.lstrip("/") if parsed.path else "postgres",
    }


def wait_for_db(max_retries: int = 30, retry_interval: int = 2):
    """Wait for database to be ready."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)

    print("Waiting for database to be ready...")
    conn_params = parse_database_url(database_url)
    print(f"Connecting to: {conn_params['host']}:{conn_params['port']}/{conn_params['database']}")

    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(**conn_params, connect_timeout=3)
            conn.close()
            print("✓ Database is ready!")
            return True
        except OperationalError as e:
            if attempt >= max_retries:
                print(f"✗ Failed to connect to database after {max_retries} attempts")
                print(f"Last error: {e}")
                sys.exit(1)
            print(f"⏳ Attempt {attempt}/{max_retries}: Database not ready yet, retrying in {retry_interval}s...")
            time.sleep(retry_interval)

    return False


if __name__ == "__main__":
    wait_for_db()
