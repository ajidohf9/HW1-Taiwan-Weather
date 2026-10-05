"""SQLite Database Module for Taiwan Weather App."""

import sqlite3
import os
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "weather.db")


def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Create a database connection and ensure directory exists."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=20.0)
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS environment_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_name TEXT NOT NULL UNIQUE,
            region TEXT,
            uv_index REAL,
            uv_level TEXT,
            uv_color TEXT,
            uv_advice TEXT,
            aqi INTEGER,
            aqi_status TEXT,
            aqi_color TEXT,
            pm25 REAL,
            pm10 REAL,
            aqi_advice TEXT,
            data_source TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forecast_7day (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_name TEXT NOT NULL,
            region TEXT,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            min_temp INTEGER,
            max_temp INTEGER,
            avg_temp INTEGER,
            apparent_min_temp INTEGER,
            apparent_max_temp INTEGER,
            rain_prob INTEGER,
            weather_state TEXT,
            relative_humidity INTEGER,
            weather_desc TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(location_name, start_time, end_time)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_title TEXT NOT NULL,
            phenomena TEXT,
            significance TEXT,
            start_time TEXT,
            end_time TEXT,
            icon TEXT,
            color TEXT,
            advice TEXT,
            location_count INTEGER,
            affected_locations TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recorded_at TIMESTAMP NOT NULL,
            location_name TEXT NOT NULL,
            region TEXT,
            avg_temp REAL,
            min_temp INTEGER,
            max_temp INTEGER,
            rain_prob INTEGER,
            weather_state TEXT,
            comfort TEXT,
            uv_index REAL,
            uv_level TEXT,
            aqi INTEGER,
            aqi_status TEXT,
            pm25 REAL,
            pm10 REAL
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_history_loc_time
        ON weather_history (location_name, recorded_at)
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_cache_meta (
            cache_key TEXT PRIMARY KEY,
            last_synced_at TIMESTAMP NOT NULL,
            ttl_seconds INTEGER DEFAULT 1800,
            item_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'OK'
        )
    """)

    conn.commit()
    conn.close()


def save_forecasts(records: List[Dict[str, Any]], db_path: str = DEFAULT_DB_PATH) -> int:
    """Save or update forecast records into the database."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    saved_count = 0
    for r in records:
        cursor.execute("""
            INSERT INTO weather_forecasts (
                location_name, region, start_time, end_time,
                weather_state, rain_prob, min_temp, max_temp, comfort, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(location_name, start_time, end_time) DO UPDATE SET
                region = excluded.region,
                weather_state = excluded.weather_state,
                rain_prob = excluded.rain_prob,
                min_temp = excluded.min_temp,
                max_temp = excluded.max_temp,
                comfort = excluded.comfort,
                updated_at = excluded.updated_at
        """, (
            r.get("location_name"),
            r.get("region", "北部"),
            r.get("start_time"),
            r.get("end_time"),
            r.get("weather_state"),
            r.get("rain_prob"),
            r.get("min_temp"),
            r.get("max_temp"),
            r.get("comfort"),
            now_str
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


def save_env_metrics(records: List[Dict[str, Any]], db_path: str = DEFAULT_DB_PATH) -> int:
    """Save or update UV and AQI environment metrics into the database."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    saved_count = 0
    for r in records:
        cursor.execute("""
            INSERT INTO environment_metrics (
                location_name, region, uv_index, uv_level, uv_color, uv_advice,
                aqi, aqi_status, aqi_color, pm25, pm10, aqi_advice, data_source, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(location_name) DO UPDATE SET
                region = excluded.region,
                uv_index = excluded.uv_index,
                uv_level = excluded.uv_level,
                uv_color = excluded.uv_color,
                uv_advice = excluded.uv_advice,
                aqi = excluded.aqi,
                aqi_status = excluded.aqi_status,
                aqi_color = excluded.aqi_color,
                pm25 = excluded.pm25,
                pm10 = excluded.pm10,
                aqi_advice = excluded.aqi_advice,
                data_source = excluded.data_source,
                updated_at = excluded.updated_at
        """, (
            r.get("location_name"),
            r.get("region", "北部"),
            r.get("uv_index"),
            r.get("uv_level"),
            r.get("uv_color"),
            r.get("uv_advice"),
            r.get("aqi"),
            r.get("aqi_status"),
            r.get("aqi_color"),
            r.get("pm25"),
            r.get("pm10"),
            r.get("aqi_advice"),
            r.get("data_source"),
            now_str
        ))
        saved_count += 1

    conn.commit()
    conn.close()
    return saved_count


def get_env_metrics(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Get all environment metrics for Taiwan counties."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM environment_metrics ORDER BY aqi ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_location_env(location_name: str, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Get environment metric for a specific location."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM environment_metrics WHERE location_name = ?", (location_name,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def save_7day_forecasts(records: List[Dict[str, Any]], db_path: str = DEFAULT_DB_PATH) -> int:
    """Save or update 7-day forecast records into the database."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    saved_count = 0
    for r in records:
        cursor.execute("""
            INSERT INTO forecast_7day (
                location_name, region, start_time, end_time,
                min_temp, max_temp, avg_temp, apparent_min_temp, apparent_max_temp,
                rain_prob, weather_state, relative_humidity, weather_desc, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(location_name, start_time, end_time) DO UPDATE SET
                region = excluded.region,
                min_temp = excluded.min_temp,
                max_temp = excluded.max_temp,
                avg_temp = excluded.avg_temp,
                apparent_min_temp = excluded.apparent_min_temp,
                apparent_max_temp = excluded.apparent_max_temp,
                rain_prob = excluded.rain_prob,
                weather_state = excluded.weather_state,
                relative_humidity = excluded.relative_humidity,
                weather_desc = excluded.weather_desc,
                updated_at = excluded.updated_at
        """, (
            r.get("location_name"),
            r.get("region", "北部"),
            r.get("start_time"),
            r.get("end_time"),
            r.get("min_temp"),
            r.get("max_temp"),
            r.get("avg_temp"),
            r.get("apparent_min_temp"),
            r.get("apparent_max_temp"),
            r.get("rain_prob"),
            r.get("weather_state"),
            r.get("relative_humidity"),
            r.get("weather_desc"),
            now_str
        ))
        saved_count += 1

    conn.commit()
    conn.close()
    return saved_count


def get_location_7day_forecast(location_name: str, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Get 7-day forecast time slots for a specific location."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM forecast_7day
        WHERE location_name = ?
        ORDER BY start_time ASC
    """, (location_name,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_7day_forecasts(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Get all 7-day forecast records."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM forecast_7day ORDER BY location_name ASC, start_time ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def save_weather_alerts(records: List[Dict[str, Any]], db_path: str = DEFAULT_DB_PATH) -> int:
    """Save latest weather warning alerts into the database, replacing previous ones."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("DELETE FROM weather_alerts")

    saved_count = 0
    for r in records:
        cursor.execute("""
            INSERT INTO weather_alerts (
                alert_title, phenomena, significance, start_time, end_time,
                icon, color, advice, location_count, affected_locations, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r.get("alert_title"),
            r.get("phenomena"),
            r.get("significance"),
            r.get("start_time"),
            r.get("end_time"),
            r.get("icon"),
            r.get("color"),
            r.get("advice"),
            r.get("location_count", 0),
            r.get("affected_locations", ""),
            now_str
        ))
        saved_count += 1

    conn.commit()
    conn.close()
    return saved_count


def get_weather_alerts(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Get active weather warning alert records."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weather_alerts ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_county_alerts_dict(db_path: str = DEFAULT_DB_PATH) -> Dict[str, List[Dict[str, Any]]]:
    """Return a mapping of county name to active alerts."""
    alerts = get_weather_alerts(db_path)
    county_map: Dict[str, List[Dict[str, Any]]] = {}

    for a in alerts:
        loc_str = a.get("affected_locations", "")
        loc_list = [loc.strip() for loc in loc_str.split(",") if loc.strip()]
        for loc in loc_list:
            if loc not in county_map:
                county_map[loc] = []
            county_map[loc].append({
                "title": a["alert_title"],
                "phenomena": a.get("phenomena", ""),
                "icon": a.get("icon", "⚠️"),
                "color": a.get("color", "#F59E0B"),
                "start_time": a.get("start_time", ""),
                "end_time": a.get("end_time", ""),
                "advice": a.get("advice", "")
            })

    return county_map


def record_history_snapshot(db_path: str = DEFAULT_DB_PATH, custom_time: str = None) -> int:
    """Record a historical snapshot for all locations using latest forecast & environment metrics."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    rec_time = custom_time if custom_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    forecasts = get_latest_forecasts(db_path)
    env_metrics = {m["location_name"]: m for m in get_env_metrics(db_path)}

    if not forecasts:
        conn.close()
        return 0

    inserted_count = 0
    for f in forecasts:
        loc = f["location_name"]
        min_t = f.get("min_temp", 20)
        max_t = f.get("max_temp", 28)
        avg_t = round((min_t + max_t) / 2.0, 1)
        rain_p = f.get("rain_prob", 0)
        state = f.get("weather_state", "晴")
        comfort = f.get("comfort", "舒適")
        region = f.get("region", "北部")

        env = env_metrics.get(loc, {})
        uv_idx = env.get("uv_index", 5.0)
        uv_lvl = env.get("uv_level", "中量級")
        aqi = env.get("aqi", 45)
        aqi_stat = env.get("aqi_status", "普通")
        pm25 = env.get("pm25", 15.0)
        pm10 = env.get("pm10", 25.0)

        cursor.execute("""
            INSERT INTO weather_history (
                recorded_at, location_name, region, avg_temp, min_temp, max_temp,
                rain_prob, weather_state, comfort, uv_index, uv_level,
                aqi, aqi_status, pm25, pm10
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rec_time, loc, region, avg_t, min_t, max_t,
            rain_p, state, comfort, uv_idx, uv_lvl,
            aqi, aqi_stat, pm25, pm10
        ))
        inserted_count += 1

    conn.commit()
    conn.close()
    return inserted_count


def seed_mock_history_if_needed(db_path: str = DEFAULT_DB_PATH, force: bool = False) -> int:
    """
    Seed realistic historical observations for past 48 hours if history table is empty.
    Creates 16 historical checkpoints (every 3 hours) with physically realistic diurnal curves.
    """
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT count(*) as cnt FROM weather_history")
    current_count = cursor.fetchone()["cnt"]

    if current_count >= 10 and not force:
        conn.close()
        return 0

    if force:
        cursor.execute("DELETE FROM weather_history")

    forecasts = get_latest_forecasts(db_path)
    env_metrics = {m["location_name"]: m for m in get_env_metrics(db_path)}

    if not forecasts:
        conn.close()
        return 0

    now = datetime.now()
    total_inserted = 0

    # 16 checkpoints covering past 48 hours (every 3 hours)
    for hours_ago in range(48, -1, -3):
        t_dt = now - timedelta(hours=hours_ago)
        rec_time = t_dt.strftime("%Y-%m-%d %H:%M:%S")
        h = t_dt.hour

        # Diurnal temperature cycle: lowest ~04:00 (-2.5C), highest ~14:00 (+2.5C)
        temp_cycle = math.sin((h - 8) / 24.0 * 2.0 * math.pi) * 2.5

        for f in forecasts:
            loc = f["location_name"]
            base_min = f.get("min_temp", 20)
            base_max = f.get("max_temp", 28)
            base_avg = (base_min + base_max) / 2.0

            loc_hash = sum(ord(c) for c in loc) % 7 - 3
            hour_noise = math.sin(hours_ago + loc_hash) * 0.8
            curr_avg = round(base_avg + temp_cycle + hour_noise, 1)
            curr_min = round(curr_avg - 2.5)
            curr_max = round(curr_avg + 2.5)

            # Rain probability with smooth fluctuations
            base_rain = f.get("rain_prob", 20)
            rain_noise = int(math.sin((hours_ago * 0.5) + loc_hash) * 15)
            curr_rain = max(0, min(100, (base_rain + rain_noise) // 5 * 5))

            # UV Index: 0 at night, bell curve between 06:00 and 18:00
            env = env_metrics.get(loc, {})
            base_uv = env.get("uv_index", 6.0)
            if 6 <= h <= 18:
                sun_factor = math.sin((h - 6) / 12.0 * math.pi)
                curr_uv = round(max(0.0, base_uv * sun_factor + (hour_noise * 0.3)), 1)
            else:
                curr_uv = 0.0

            if curr_uv >= 11:
                uv_lvl = "危險級"
            elif curr_uv >= 8:
                uv_lvl = "過量級"
            elif curr_uv >= 6:
                uv_lvl = "高量級"
            elif curr_uv >= 3:
                uv_lvl = "中量級"
            else:
                uv_lvl = "微量級"

            # AQI: realistic diurnal cycle with rush hour boosts
            base_aqi = env.get("aqi", 45)
            rush_hour_boost = 10 if (7 <= h <= 9 or 17 <= h <= 20) else 0
            curr_aqi = max(15, min(180, int(base_aqi + rush_hour_boost + (hour_noise * 4))))

            if curr_aqi <= 50:
                aqi_stat = "良好"
            elif curr_aqi <= 100:
                aqi_stat = "普通"
            elif curr_aqi <= 150:
                aqi_stat = "對敏感族群不健康"
            else:
                aqi_stat = "對所有族群不健康"

            pm25 = round(max(5.0, curr_aqi * 0.28 + (hour_noise * 1.5)), 1)
            pm10 = round(max(10.0, curr_aqi * 0.55 + (hour_noise * 2.0)), 1)

            cursor.execute("""
                INSERT INTO weather_history (
                    recorded_at, location_name, region, avg_temp, min_temp, max_temp,
                    rain_prob, weather_state, comfort, uv_index, uv_level,
                    aqi, aqi_status, pm25, pm10
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rec_time, loc, f.get("region", "北部"), curr_avg, curr_min, curr_max,
                curr_rain, f.get("weather_state", "晴"), f.get("comfort", "舒適"),
                curr_uv, uv_lvl, curr_aqi, aqi_stat, pm25, pm10
            ))
            total_inserted += 1

    conn.commit()
    conn.close()
    return total_inserted


def get_location_history(location_name: str, limit_records: int = 100, limit: Optional[int] = None, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Get chronological historical observation records for a specific location."""
    if limit is not None:
        limit_records = limit
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM weather_history
        WHERE location_name = ?
        ORDER BY recorded_at ASC
        LIMIT ?
    """, (location_name, limit_records))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_multi_location_history(location_names: List[str], db_path: str = DEFAULT_DB_PATH, **kwargs) -> List[Dict[str, Any]]:
    """Get historical records for multiple locations."""
    init_db(db_path)
    if not location_names:
        return []
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    placeholders = ",".join("?" for _ in location_names)
    query = f"""
        SELECT * FROM weather_history
        WHERE location_name IN ({placeholders})
        ORDER BY recorded_at ASC, location_name ASC
    """
    cursor.execute(query, location_names)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_history(limit: Any = 1000, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Get all history records ordered by newest first. Supports limit as first argument or keyword."""
    if isinstance(limit, str):
        actual_db_path = limit
        actual_limit = db_path if isinstance(db_path, int) else 1000
    else:
        actual_limit = int(limit) if limit is not None else 1000
        actual_db_path = db_path if isinstance(db_path, str) else DEFAULT_DB_PATH

    init_db(actual_db_path)
    conn = get_db_connection(actual_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weather_history ORDER BY recorded_at DESC, location_name ASC LIMIT ?", (actual_limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def clear_history(db_path: str = DEFAULT_DB_PATH) -> int:
    """Clear all records from weather_history."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM weather_history")
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted


def update_cache_meta(
    cache_key: str,
    item_count: int = 0,
    ttl_seconds: int = 1800,
    status: str = "OK",
    db_path: str = DEFAULT_DB_PATH
):
    """Update or insert cache metadata for a specific dataset."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO system_cache_meta (cache_key, last_synced_at, ttl_seconds, item_count, status)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(cache_key) DO UPDATE SET
            last_synced_at = excluded.last_synced_at,
            ttl_seconds = excluded.ttl_seconds,
            item_count = excluded.item_count,
            status = excluded.status
    """, (cache_key, now_str, ttl_seconds, item_count, status))
    conn.commit()
    conn.close()


def get_all_cache_meta(db_path: str = DEFAULT_DB_PATH) -> Dict[str, Dict[str, Any]]:
    """Get all cache metadata records."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM system_cache_meta ORDER BY cache_key ASC")
    rows = cursor.fetchall()
    conn.close()
    return {row["cache_key"]: dict(row) for row in rows}


def get_data_freshness_status(
    cache_key: str = "global_sync",
    default_ttl: int = 1800,
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """Calculate real-time data freshness, elapsed time, and cache TTL countdown."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM system_cache_meta WHERE cache_key = ?", (cache_key,))
    row = cursor.fetchone()

    last_time_str = None
    ttl_seconds = default_ttl

    if row:
        last_time_str = row["last_synced_at"]
        ttl_seconds = row["ttl_seconds"]
    else:
        # Fallback to MAX(updated_at) or MAX(recorded_at)
        cursor.execute("SELECT MAX(updated_at) as max_up FROM weather_forecasts")
        r_up = cursor.fetchone()
        if r_up and r_up["max_up"]:
            last_time_str = r_up["max_up"]
        else:
            cursor.execute("SELECT MAX(recorded_at) as max_rec FROM weather_history")
            r_rec = cursor.fetchone()
            if r_rec and r_rec["max_rec"]:
                last_time_str = r_rec["max_rec"]

    conn.close()

    now = datetime.now()
    if last_time_str:
        try:
            t_clean = str(last_time_str).split(".")[0].replace("T", " ")
            last_dt = datetime.strptime(t_clean, "%Y-%m-%d %H:%M:%S")
            diff_sec = max(0, int((now - last_dt).total_seconds()))
        except Exception:
            diff_sec = 0
            last_dt = now
    else:
        diff_sec = 0
        last_dt = now

    minutes_ago = diff_sec // 60
    hours_ago = minutes_ago // 60
    remaining_sec = max(0, ttl_seconds - diff_sec)

    if minutes_ago < 1:
        elapsed_text = "剛剛 (< 1 分鐘前)"
    elif minutes_ago < 60:
        elapsed_text = f"{minutes_ago} 分鐘前"
    elif hours_ago < 24:
        elapsed_text = f"{hours_ago} 小時 {minutes_ago % 60} 分鐘前"
    else:
        elapsed_text = f"{hours_ago // 24} 天前"

    is_fresh = diff_sec < ttl_seconds
    if diff_sec <= 900:  # <= 15 分鐘
        level = "fresh"
        color = "#10B981"
        badge_text = f"🟢 即時最新 ({elapsed_text})"
        status_label = "即時新鮮 (無需同步)"
    elif is_fresh:  # 快取時限內
        level = "good"
        color = "#38BDF8"
        badge_text = f"🔵 良好快取 ({elapsed_text})"
        status_label = "有效快取 (運作順暢)"
    elif diff_sec <= ttl_seconds * 2:
        level = "warn"
        color = "#F59E0B"
        badge_text = f"🟡 建議更新 ({elapsed_text})"
        status_label = "快取即將過期"
    else:
        level = "stale"
        color = "#EF4444"
        badge_text = f"🔴 資料已過期 ({elapsed_text})"
        status_label = "已過期 (建議重新同步)"

    return {
        "cache_key": cache_key,
        "last_synced_at": last_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_seconds": diff_sec,
        "elapsed_minutes": minutes_ago,
        "elapsed_text": elapsed_text,
        "remaining_seconds": remaining_sec,
        "remaining_minutes": remaining_sec // 60,
        "ttl_seconds": ttl_seconds,
        "is_fresh": is_fresh,
        "level": level,
        "color": color,
        "badge_text": badge_text,
        "status_label": status_label
    }




