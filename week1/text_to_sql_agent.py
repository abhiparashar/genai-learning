import os
from dotenv import load_dotenv
import google.generativeai as genai
import psycopg2
import json

# Load environment variables
load_dotenv()

# Configure Gemini
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
        print(f"❌ Database connection failed: {e}")
        return None
    
def is_safe_query(sql):
    """Check if SQL query is safe (only SELECT allowed)"""
    # Convert to uppercase for checking
    sql_upper = sql.upper().strip()
    
    # Dangerous keywords that should NOT be in the query
    dangerous_keywords = ['DELETE', 'DROP', 'INSERT', 'UPDATE', 'ALTER', 'TRUNCATE', 'EXEC', 'EXECUTE']
    
    # Check if query starts with SELECT
    if not sql_upper.startswith('SELECT'):
        return False
    
    # Check for dangerous keywords
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return False
    
    return True

# System prompt for Gemini - teaches it how to generate SQL
SYSTEM_PROMPT = """You are a PostgreSQL expert. Generate safe SQL queries.

Database Schema:
1. customers table: id, name, email, city, state, signup_date
2. products table: id, name, category, price, stock
3. orders table: id, customer_id, product_id, quantity, total_amount, order_date, status

Rules:
- Only generate SELECT queries
- Use proper table and column names
- Add LIMIT 100 to all queries (safety)
- Return ONLY the SQL query, nothing else
- Use JOIN when needed to combine tables

Examples:
Question: "Show all customers from California"
SQL: SELECT * FROM customers WHERE state = 'California' LIMIT 100;

Question: "What products cost more than $500?"
SQL: SELECT * FROM products WHERE price > 500 LIMIT 100;

Now generate SQL for the user's question."""

# Store conversation history
conversation_history = []
last_query_result = None

def text_to_sql(question, context=""):
    """Convert natural language question to SQL query using Gemini"""
    try:
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        
        # Make the prompt very explicit
        if context:
            full_prompt = f"""{context}

User's new question: {question}

IMPORTANT: If the question uses words like "they", "them", "those", "it", "how many", you MUST apply the same WHERE conditions from the previous SQL query."""
        else:
            full_prompt = question
        
        response = model.generate_content(full_prompt)
        sql = response.text.strip()
        sql = sql.replace('```sql', '').replace('```', '').strip()
        
        return sql
    except Exception as e:
        print(f"❌ Error generating SQL: {e}")
        return None
    
    
def execute_query(sql):
    """Execute SQL query and return results"""
    # First check if query is safe
    if not is_safe_query(sql):
        return {"error": "Unsafe query detected! Only SELECT queries are allowed."}
    
    # Connect to database
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed"}
    
    try:
        # Create cursor and execute query
        cursor = conn.cursor()
        cursor.execute(sql)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch all results
        rows = cursor.fetchall()
        
        # Close connections
        cursor.close()
        conn.close()
        
        # Return results as list of dictionaries
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        
        return {"success": True, "data": results, "count": len(results)}
        
    except Exception as e:
        conn.close()
        return {"error": f"Query execution failed: {e}"}
    
def export_results(data, format='csv', filename='results'):
    """Export query results to file"""
    import pandas as pd
    from datetime import datetime
    
    if not data:
        print("❌ No data to export")
        return
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add timestamp to filename
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
        
        print(f"✅ Exported to: {file}")
    except Exception as e:
        print(f"❌ Export failed: {e}")

def generate_chart(data, chart_type='bar'):
    """Generate chart from query results"""
    import matplotlib.pyplot as plt
    import pandas as pd
    from datetime import datetime
    
    if not data or len(data) < 2:
        print("❌ Need at least 2 rows to generate chart")
        return
    
    df = pd.DataFrame(data)
    
    # Get numeric columns
    numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32']).columns
    
    if len(numeric_cols) == 0:
        print("❌ No numeric data to visualize")
        return
    
    try:
        # Use first column as X-axis, first numeric as Y-axis
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
        
        # Save chart
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"chart_{timestamp}.png"
        plt.savefig(filename)
        print(f"✅ Chart saved: {filename}")
        plt.close()
        
    except Exception as e:
        print(f"❌ Chart generation failed: {e}")

    
def main():
    """Main function - interactive Text-to-SQL agent"""
    print("=" * 50)
    print("🤖 Text-to-SQL Agent")
    print("=" * 50)
    print("Ask questions about your e-commerce data!")
    print("Type 'exit' to quit\n")
    
    while True:
        # Get user question
        question = input("You: ").strip()
        
        # Exit command
        if question.lower() == 'exit':
            print("👋 Goodbye!")
            break
        
        # Clear history command
        if question.lower() == 'clear':
            conversation_history.clear()
            last_query_result = None
            print("🗑️ History cleared!\n")
            continue
        
        if not question:
            continue
        
        print("\n🔄 Converting to SQL...")
        
       # Build context from history
        context = ""
        if conversation_history:
            last_item = conversation_history[-1]
            context = f"""The user just asked: "{last_item['question']}"
Which generated this SQL: {last_item['sql']}
This returned {last_item['result_count']} results.

If the new question refers to "they", "them", "those", "it", use the WHERE clause from the previous SQL."""
        
        # Step 1: Convert question to SQL with context
        sql = text_to_sql(question, context)
        if not sql:
            print("❌ Could not generate SQL\n")
            continue
        
        print(f"📝 Generated SQL: {sql}\n")
        
        # Step 2: Execute SQL
        print("⚡ Executing query...")
        result = execute_query(sql)
        
        # Save to history
        conversation_history.append({
            'question': question,
            'sql': sql,
            'result_count': result.get('count', 0)
        })
        last_query_result = result
        
        # Step 3: Display results
        if "error" in result:
            print(f"❌ {result['error']}\n")
        else:
            print(f"✅ Found {result['count']} results:")
            for i, row in enumerate(result['data'], 1):
                print(f"{i}. {row}")
            
            # Ask if user wants to export
            if result['count'] > 0:
                export = input("\n💾 Export results? (csv/json/excel/no): ").strip().lower()
                if export in ['csv', 'json', 'excel']:
                    export_results(result['data'], format=export)
                
                # Ask if user wants to visualize
                chart = input("📊 Create chart? (bar/line/pie/no): ").strip().lower()
                if chart in ['bar', 'line', 'pie']:
                    generate_chart(result['data'], chart_type=chart)
            print()        # Get user question
        question = input("You: ").strip()
        
        # Exit command
        if question.lower() == 'exit':
            print("👋 Goodbye!")
            break
        
        if not question:
            continue
        
        print("\n🔄 Converting to SQL...")
        
        # Step 1: Convert question to SQL
        sql = text_to_sql(question)
        if not sql:
            print("❌ Could not generate SQL\n")
            continue
        
        print(f"📝 Generated SQL: {sql}\n")
        
        # Step 2: Execute SQL
        print("⚡ Executing query...")
        result = execute_query(sql)
        
      # Step 3: Display results
        if "error" in result:
            print(f"❌ {result['error']}\n")
        else:
            print(f"✅ Found {result['count']} results:")
            for i, row in enumerate(result['data'], 1):
                print(f"{i}. {row}")
            
           # Ask if user wants to export
            if result['count'] > 0:
                export = input("\n💾 Export results? (csv/json/excel/no): ").strip().lower()
                if export in ['csv', 'json', 'excel']:
                    export_results(result['data'], format=export)
                
                # Ask if user wants to visualize
                chart = input("📊 Create chart? (bar/line/pie/no): ").strip().lower()
                if chart in ['bar', 'line', 'pie']:
                    generate_chart(result['data'], chart_type=chart)
            print()


# Run the agent
if __name__ == "__main__":
    main()