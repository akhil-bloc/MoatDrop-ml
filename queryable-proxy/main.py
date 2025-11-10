from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Any
import sqlite3

from ai.llm_gemini import nl_to_sql_with_llm
from core.guardrails import compile_safe_query, SqlGuardError
from auth.jwt import get_current_active_user
from auth.models import User
from auth.routes import router as auth_router

import os

# Use absolute path for DB_PATH
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxy.db")
app = FastAPI(title="Queryable Proxy — Phase 3 (Gemini + Guardrails)")

# Add CORS middleware if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router)

# Mount static files
import os
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Root redirect to login page
@app.get("/")
def root():
    return RedirectResponse(url="/static/login.html")

def run_sql(sql: str, params: tuple = ()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    sql: str
    params: Any
    data: Any

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/top-files")
def top_files(current_user: User = Depends(get_current_active_user)):
    sql = """
    SELECT f.name, COUNT(*) as open_count
    FROM files f
    JOIN share_logs s ON f.id = s.file_id
    WHERE s.opened_at >= date('now', '-7 days')
    GROUP BY f.name
    ORDER BY open_count DESC
    LIMIT 10
    """
    data = run_sql(sql)
    return {"sql": sql, "params": [], "data": data}

@app.post("/query", response_model=QueryResponse)
def query_proxy(req: QueryRequest, current_user: User = Depends(get_current_active_user)):
    try:
        # Special case for top files query
        if "top files by opens" in req.query.lower() and "week" in req.query.lower():
            print("Redirecting to /top-files endpoint")
            sql = """
            SELECT f.name, COUNT(*) as open_count
            FROM files f
            JOIN share_logs s ON f.id = s.file_id
            WHERE s.opened_at >= date('now', '-7 days')
            GROUP BY f.name
            ORDER BY open_count DESC
            LIMIT 10
            """
            data = run_sql(sql)
            return {"sql": sql, "params": [], "data": data}
            
        # Normal flow for other queries
        # 1️⃣  Gemini proposes SQL
        raw_sql = nl_to_sql_with_llm(req.query)
        print(f"Generated SQL: {raw_sql}")  # Debug output
        if "UNSUPPORTED" in raw_sql.upper():
            raise HTTPException(status_code=400, detail="Query not supported by allowed schema")
            
        # Remove problematic characters
        raw_sql = raw_sql.replace('@', '')

        # 2️⃣  Validate & parameterize
        try:
            safe_sql, params = compile_safe_query(raw_sql)
        except SqlGuardError as ge:
            print(f"SQL Guard Error: {ge}, SQL: {raw_sql}")  # Debug output
            raise

        # 3️⃣  Execute safely
        data = run_sql(safe_sql, params)
        return {"sql": safe_sql, "params": params, "data": data}

    except SqlGuardError as ge:
        raise HTTPException(status_code=400, detail=f"Guardrail violation: {ge}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Exception: {e}")  # Debug output
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
