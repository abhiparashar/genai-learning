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

def text_to_sql(question):
    """Convert natural language question to SQL query using Gemini"""
    try:
        # Create model with system instruction
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        
        # Generate SQL from question
        response = model.generate_content(question)
        sql = response.text.strip()
        
        # Clean up the SQL (remove markdown code blocks if present)
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
            print()


# Run the agent
if __name__ == "__main__":
    main()