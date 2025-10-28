import re
from datetime import datetime, timedelta
from core.database import run_sql, last_week_timestamp
from data.mock_api import fetch_user_metrics

def route_query(user_query: str):
    """
    Interprets the user's query and decides which data sources to call.
    Can call: SQLite, Mock API, or both.
    """
    q = user_query.lower().strip()

    # ----------------------------
    # Example 1: Files-related query → SQLite only
    # ----------------------------
    if "file" in q:
        if "opened more than" in q:
            m = re.search(r"(more than|over)\s+(\d+)\s+times", q)
            threshold = int(m.group(2)) if m else 1
            sql = """
                SELECT f.name, COUNT(s.id) AS opens
                FROM files f
                JOIN share_logs s ON s.file_id = f.id
                GROUP BY f.id
                HAVING COUNT(s.id) > ?
                ORDER BY opens DESC;
            """
            return run_sql(sql, (threshold,))

        if "top files" in q:
            sql = """
                SELECT f.name, COUNT(s.id) AS opens
                FROM files f
                LEFT JOIN share_logs s ON s.file_id = f.id
                GROUP BY f.id
                ORDER BY opens DESC;
            """
            return run_sql(sql)

    # ----------------------------
    # Example 2: User metrics → Mock API only
    # ----------------------------
    if "user" in q and "metrics" in q:
        return fetch_user_metrics()

    # ----------------------------
    # Example 3: Combined query (merge both)
    # ----------------------------
    if "file" in q and "engagement" in q:
        sql = """
            SELECT DISTINCT s.viewer_email AS email, COUNT(s.id) AS opens
            FROM share_logs s
            WHERE s.opened_at >= ?
            GROUP BY s.viewer_email;
        """
        file_stats = run_sql(sql, (last_week_timestamp(),))
        user_metrics = fetch_user_metrics()
        return merge_results(file_stats, user_metrics)

    raise ValueError("Unsupported query pattern")

def merge_results(file_stats, user_metrics):
    """
    Merge results from both sources by email (like a join).
    """
    merged = []
    for f in file_stats:
        for u in user_metrics:
            if f["email"] == u["email"]:
                merged.append({
                    "email": f["email"],
                    "opens": f["opens"],
                    "engagement_score": u["engagement_score"],
                    "last_active": u["last_active"]
                })
    return merged
