import random
from datetime import datetime, timedelta

def fetch_user_metrics():
    """Pretend this calls an external REST API."""
    users = ["josh@example.com", "tyler@example.com", "ceo@invest.com"]
    metrics = []
    for u in users:
        metrics.append({
            "email": u,
            "engagement_score": random.randint(60, 100),
            "last_active": (datetime.utcnow() - timedelta(days=random.randint(1, 10))).isoformat()
        })
    return metrics
