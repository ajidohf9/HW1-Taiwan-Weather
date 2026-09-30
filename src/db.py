"""SQLite Database Module for Taiwan Weather App."""

import sqlite3
import os
from typing import List, Dict, Any, Optional

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "weather.db")


def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Create a database connection and ensure directory exists."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH):
    """Initialize database tables."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_name TEXT NOT NULL,
            region TEXT,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            weather_state TEXT,
            rain_prob INTEGER,
            min_temp INTEGER,
            max_temp INTEGER,
            comfort TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(location_name, start_time, end_time)
        )
    """)

    conn.commit()
    conn.close()


def save_forecasts(records: List[Dict[str, Any]], db_path: str = DEFAULT_DB_PATH) -> int:
    """Save or update forecast records into the database."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    saved_count = 0
    for r in records:
        cursor.execute("""
            INSERT INTO weather_forecasts (
                location_name, region, start_time, end_time,
                weather_state, rain_prob, min_temp, max_temp, comfort, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(location_name, start_time, end_time) DO UPDATE SET
                region = excluded.region,
                weather_state = excluded.weather_state,
                rain_prob = excluded.rain_prob,
                min_temp = excluded.min_temp,
                max_temp = excluded.max_temp,
                comfort = excluded.comfort,
                updated_at = CURRENT_TIMESTAMP
        """, (
            r.get("location_name"),
            r.get("region", "北部"),
            r.get("start_time"),
            r.get("end_time"),
            r.get("weather_state"),
            r.get("rain_prob"),
            r.get("min_temp"),
            r.get("max_temp"),
            r.get("comfort")
        ))
        saved_count += 1

    conn.commit()
    conn.close()
    return saved_count


def get_all_locations(db_path: str = DEFAULT_DB_PATH) -> List[str]:
    """Get list of distinct location names."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT location_name FROM weather_forecasts ORDER BY location_name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [row["location_name"] for row in rows]


def get_latest_forecasts(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Get the earliest active forecast slice for all locations."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Select the earliest start_time per location
    query = """
        SELECT wf.*
        FROM weather_forecasts wf
        INNER JOIN (
            SELECT location_name, MIN(start_time) as min_start
            FROM weather_forecasts
            GROUP BY location_name
        ) latest
        ON wf.location_name = latest.location_name AND wf.start_time = latest.min_start
        ORDER BY wf.location_name ASC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_location_forecast(location_name: str, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Get all forecast periods for a specific location."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM weather_forecasts
        WHERE location_name = ?
        ORDER BY start_time ASC
    """, (location_name,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
