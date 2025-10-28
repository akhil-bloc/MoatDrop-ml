import os
import google.generativeai as genai
from textwrap import dedent
from core.schema_policy import schema_description
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize model (use gemini-2.5-flash for speed, gemini-2.5-pro for higher accuracy)
MODEL = genai.GenerativeModel("gemini-2.5-flash")

SYSTEM_PROMPT = dedent(f"""
You are a SQL generator for a SQLite database.

Return ONLY raw SQL (no markdown, no backticks, no explanations).

Rules:
- Use ONLY the allowed schema below.
- Only SELECT statements are allowed.
- JOIN only on whitelisted keys.
- If the request is unsupported, reply: SELECT 'UNSUPPORTED' AS error;
- Add LIMIT <=200 if missing.

Allowed schema:
{schema_description()}
""").strip()

def nl_to_sql_with_llm(user_query: str) -> str:
    """Use Gemini to convert NL → SQL under the above guardrails."""
    user_prompt = dedent(f"""
    User question:
    {user_query}

    Generate a single valid SQLite SELECT query that answers the question,
    obeying every rule in the system instructions above.
    """).strip()

    try:
        response = MODEL.generate_content(
            [SYSTEM_PROMPT, user_prompt],
            generation_config=genai.types.GenerationConfig(
                temperature=0.0,
                max_output_tokens=512,
            ),
        )

        sql = response.text.strip()
        if sql.startswith("```"):
            sql = sql.strip("`").split("\n", 1)[-1]
        
        print(f"Generated SQL: {sql}")
        return sql
    except Exception as e:
        print(f"Error generating SQL: {e}")
        return "SELECT 'UNSUPPORTED' AS error;"
