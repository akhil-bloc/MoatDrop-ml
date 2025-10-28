ALLOWED_SCHEMA = {
    "files": ["id", "name", "created_at"],
    "share_logs": ["id", "file_id", "viewer_email", "opened_at"],
}

# Optional: expose a human-readable summary for the LLM
def schema_description() -> str:
    lines = []
    lines.append("tables:")
    for t, cols in ALLOWED_SCHEMA.items():
        lines.append(f"- {t}({', '.join(cols)})")
    lines.append("""
relationships:
- share_logs.file_id -> files.id
notes:
- timestamps are ISO8601 strings
- use date(opened_at) for day-level filters
- default to LIMIT 100 if not specified
""")
    return "\n".join(lines)
