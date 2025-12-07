import os
from dotenv import load_dotenv
import google.generativeai as genai
import psycopg2

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_db_connection():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None
    
def is_safe_query(sql):
    """Check if SQL query is safe (only SELECT allowed)"""
    sql_upper = sql.upper().strip()
    dangerous_keywords = ['DELETE', 'DROP', 'INSERT', 'UPDATE', 'ALTER', 'TRUNCATE', 'EXEC', 'EXECUTE']
    
    if not sql_upper.startswith('SELECT'):
        return False
    
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return False
    
    return True

SYSTEM_PROMPT = """You are a PostgreSQL expert. Generate safe SQL queries.

Database Schema:
1. customers table: id, name, email, city, state, signup_date
2. products table: id, name, category, price, stock
3. orders table: id, customer_id, product_id, quantity, total_amount, order_date, status

Rules:
- Only generate SELECT queries
- Add LIMIT 100
- Return only SQL
- Use correct schema
"""

conversation_history = []
last_query_result = None

def text_to_sql(question, context=""):
    try:
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        
        if context:
            full_prompt = f"""{context}

User question: {question}

If the user uses words like 'they', 'it', apply previous WHERE clause."""
        else:
            full_prompt = question
        
        response = model.generate_content(full_prompt)
        sql = response.text.strip().replace('```sql', '').replace('```', '').strip()
        return sql

    except Exception as e:
        print(f"Error generating SQL: {e}")
        return None
    
def execute_query(sql):
    if not is_safe_query(sql):
        return {"error": "Unsafe query. Only SELECT allowed."}
    
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed"}
    
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        results = [dict(zip(columns, row)) for row in rows]
        
        return {"success": True, "data": results, "count": len(results)}
        
    except Exception as e:
        conn.close()
        return {"error": f"Query execution failed: {e}"}

def export_results(data, format='csv', filename='results'):
    import pandas as pd
    from datetime import datetime
    
    if not data:
        print("No data to export")
        return
    
    df = pd.DataFrame(data)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    try:
        if format == 'csv':
            file = f"{filename}_{timestamp}.csv"
            df.to_csv(file, index=False)
        elif format == 'json':
            file = f"{filename}_{timestamp}.json"
            df.to_json(file, orient='records', indent=2)
        elif format == 'excel':
            file = f"{filename}_{timestamp}.xlsx"
            df.to_excel(file, index=False)
        
        print(f"Exported to: {file}")
    except Exception as e:
        print(f"Export failed: {e}")

def generate_chart(data, chart_type='bar'):
    import matplotlib.pyplot as plt
    import pandas as pd
    from datetime import datetime
    
    if not data or len(data) < 2:
        print("Not enough data for chart")
        return
    
    df = pd.DataFrame(data)
    
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    
    if len(numeric_cols) == 0:
        print("No numeric data to visualize")
        return
    
    try:
        x_col = df.columns[0]
        y_col = numeric_cols[0]
        
        plt.figure(figsize=(10, 6))
        
        if chart_type == 'bar':
            plt.bar(df[x_col].astype(str), df[y_col])
        elif chart_type == 'line':
            plt.plot(df[x_col].astype(str), df[y_col], marker='o')
        elif chart_type == 'pie':
            plt.pie(df[y_col], labels=df[x_col].astype(str), autopct='%1.1f%%')
        
        plt.title(f'{y_col} by {x_col}')
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"chart_{timestamp}.png"
        
        plt.savefig(filename)
        print(f"Chart saved: {filename}")
        plt.close()
        
    except Exception as e:
        print(f"Chart generation failed: {e}")

def main():
    print("Text-to-SQL Agent")
    print("Type 'exit' to quit\n")
    
    while True:
        question = input("You: ").strip()
        
        if question.lower() == 'exit':
            print("Goodbye")
            break
        
        if question.lower() == 'clear':
            conversation_history.clear()
            last_query_result = None
            print("History cleared\n")
            continue
        
        if not question:
            continue
        
        print("Generating SQL...")
        
        context = ""
        if conversation_history:
            last_item = conversation_history[-1]
            context = f"""Previous question: {last_item['question']}
Previous SQL: {last_item['sql']}
Previous results: {last_item['result_count']}"""
        
        sql = text_to_sql(question, context)
        if not sql:
            print("Failed to generate SQL\n")
            continue
        
        print(f"SQL: {sql}\n")
        
        print("Executing query...")
        result = execute_query(sql)
        
        conversation_history.append({
            'question': question,
            'sql': sql,
            'result_count': result.get('count', 0)
        })
        
        if "error" in result:
            print(result['error'], "\n")
        else:
            print(f"Rows: {result['count']}")
            for i, row in enumerate(result['data'], 1):
                print(f"{i}. {row}")
            
            if result['count'] > 0:
                export = input("\nExport (csv/json/excel/no): ").strip().lower()
                if export in ['csv', 'json', 'excel']:
                    export_results(result['data'], format=export)
                
                chart = input("Chart (bar/line/pie/no): ").strip().lower()
                if chart in ['bar', 'line', 'pie']:
                    generate_chart(result['data'], chart_type=chart)
            print()

if __name__ == "__main__":
    main()