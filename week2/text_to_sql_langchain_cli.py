# Ensure langchain global attributes exist BEFORE importing any langchain-related packages
import langchain
if not hasattr(langchain, "verbose"):
    langchain.verbose = False
    langchain.debug = False
    langchain.llm_cache = False

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from dotenv import load_dotenv
import psycopg2
import os
import pandas as pd
from datetime import datetime

load_dotenv()

# LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0
)

# DB config
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "ecommerce_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD")
}

# Global state
last_results = None
last_sql = None
conversation_history = []

# ---------- TOOLS ----------


@tool
def get_schema() -> str:
    """Return database schema: tables, columns and data types."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columnsA
        WHERE table_schema='public'
        ORDER BY table_name, ordinal_position
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    output = ["Database Schema:"]
    current_table = None
    for table, col, dtype in rows:
        if current_table != table:
            output.append(f"\n{table}:")
            current_table = table
        output.append(f"  - {col} ({dtype})")
    return "\n".join(output)


@tool
def execute_sql(sql: str) -> str:
    """Execute a safe SELECT query and return results as formatted text."""
    global last_results, last_sql

    sql_clean = sql.strip().upper()
    if not sql_clean.startswith("SELECT"):
        return "Error: Only SELECT queries allowed."

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        cur.close()
        conn.close()

        if not rows:
            last_results = None
            last_sql = None
            return "No results."

        last_results = pd.DataFrame(rows, columns=cols)
        last_sql = sql

        return f"Rows: {len(rows)}\n\n{last_results.to_string()}"

    except Exception as e:
        return f"SQL Error: {str(e)}"


# Bind tools
llm_with_tools = llm.bind_tools([get_schema, execute_sql])


# ---------- AGENT LOOP ----------
def run_agent(question: str) -> str:
    conversation_history.append({"role": "user", "content": question})
    messages = conversation_history.copy()

    for _ in range(5):
        response = llm_with_tools.invoke(messages)

        if response.tool_calls:
            tool_call = response.tool_calls[0]
            name = tool_call["name"]
            args = tool_call.get("args", {})

            if name == "get_schema":
                result = get_schema.invoke(args)
            elif name == "execute_sql":
                result = execute_sql.invoke(args)
            else:
                result = f"Unknown tool: {name}"

            messages.append({
                "role": "assistant",
                "content": response.content,
                "tool_calls": response.tool_calls
            })
            messages.append({
                "role": "tool",
                "content": result,
                "tool_call_id": tool_call.get("id")
            })
            continue

        txt = response.content if isinstance(response.content, str) else response.content[0].get("text")
        conversation_history.append({"role": "assistant", "content": txt})
        return txt

    return "Max iterations reached."


# ---------- EXPORT ----------
def export_results(fmt="csv"):
    if last_results is None:
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    if fmt == "csv":
        fn = f"results_{ts}.csv"
        last_results.to_csv(fn, index=False)
    elif fmt == "excel":
        fn = f"results_{ts}.xlsx"
        last_results.to_excel(fn, index=False)
    elif fmt == "json":
        fn = f"results_{ts}.json"
        last_results.to_json(fn, orient="records", indent=2)
    else:
        return

    print(fn)


# ---------- VISUALIZE ----------
def visualize_results():
    if last_results is None:
        return

    if len(last_results.columns) != 2:
        return

    import matplotlib.pyplot as plt

    df = last_results.copy()
    x, y = df.columns[0], df.columns[1]

    try:
        df[y] = df[y].astype(str).str.replace("$", "").str.replace(",", "").astype(float)
    except:
        pass

    df = df.dropna(subset=[y])
    if df.empty:
        return

    df.plot(kind="bar", x=x, y=y, legend=False)
    plt.tight_layout()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fn = f"chart_{ts}.png"
    plt.savefig(fn)
    plt.close()

    print(fn)


# ---------- HISTORY ----------
def show_history():
    if not conversation_history:
        return
    for i, m in enumerate(conversation_history, 1):
        content = str(m['content'])[:180]
        print(f"[{i}] {m['role']}: {content}")


def clear_history():
    global conversation_history
    conversation_history = []


# ---------- CLI ----------
def main():
    print("Ready")
    while True:
        try:
            q = input().strip()
            if not q:
                continue

            if q == "/exit":
                break
            elif q.startswith("/export"):
                parts = q.split()
                fmt = parts[1] if len(parts) > 1 else "csv"
                export_results(fmt)
                continue
            elif q == "/viz":
                visualize_results()
                continue
            elif q == "/history":
                show_history()
                continue
            elif q == "/clear":
                clear_history()
                continue

            ans = run_agent(q)
            print(ans)

        except KeyboardInterrupt:
            break
        except Exception:
            break


if __name__ == "__main__":
    main()
