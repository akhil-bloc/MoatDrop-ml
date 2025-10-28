import sqlite3
from datetime import datetime, timedelta

DB_PATH = "proxy.db"

def run_sql(sql: str, params: tuple = ()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def last_week_timestamp():
    return (datetime.utcnow() - timedelta(days=7)).isoformat()
