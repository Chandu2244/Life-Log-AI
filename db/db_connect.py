import sqlite3
import json
import os

# Database stored in db folder
DB_PATH = os.path.join(os.path.dirname(__file__), "life_log.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "create_tables.sql")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-style fetching
    return conn


def init_database():
    """Create tables if they do not exist."""
    with get_connection() as conn:
        cur = conn.cursor()
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            cur.executescript(f.read())
        conn.commit()
        print("✔ Database initialized successfully!")


def insert_raw_day(journal_date: str, merged_content: list):
    """Insert or update raw daily journal input."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO journal_day_raw (journal_date, merged_content)
            VALUES (?, ?)
            ON CONFLICT(journal_date) DO UPDATE SET
                merged_content = excluded.merged_content
        """, (journal_date, json.dumps(merged_content)))
        conn.commit()


def insert_processed_section(journal_date: str, category: str, content_lines: list):
    """Insert NLP processed categorized content."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO journal_day_processed (journal_date, category, content_lines)
            VALUES (?, ?, ?)
        """, (journal_date, category, json.dumps(content_lines)))
        conn.commit()


def insert_weekly_stats(year: int, week_number: int, category: str, count: int):
    """Insert or update weekly habit stats for fast dashboard queries."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO weekly_habit_stats (year, week_number, category, count)
            VALUES (?, ?, ?, ?)
        """, (year, week_number, category, count))
        conn.commit()
