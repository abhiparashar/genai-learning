from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from dotenv import load_dotenv
import psycopg2
import os
import pandas as pd
import json
from datetime import datetime

# Load env
load_dotenv()

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv('GEMINI_API_KEY'),
    temperature=0
)

# Database config
DB_CONFIG = {
    'host': 'localhost',
    'database': 'ecommerce_db',
    'user': 'postgres',
    'password': os.getenv('DB_PASSWORD')
}

# Store last query results globally
last_results = None
last_sql = None

# Tool 1: Get Schema
@tool
def get_schema() -> str:
    """Get database schema with table and column information"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT table_name, column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
    """)
    
    schema = cur.fetchall()
    cur.close()
    conn.close()
    
    result = "Database Schema:\n"
    current_table = None
    for table, column, dtype in schema:
        if table != current_table:
            result += f"\n{table}:\n"
            current_table = table
        result += f"  - {column} ({dtype})\n"
    
    return result

# Tool 2: Execute SQL (safe)
@tool
def execute_sql(sql: str) -> str:
    """Execute SELECT queries only. Returns results as text."""
    global last_results, last_sql
    
    if not sql.strip().upper().startswith('SELECT'):
        return "Error: Only SELECT queries allowed"
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(sql)
        results = cur.fetchall()
        
        # Get column names
        colnames = [desc[0] for desc in cur.description]
        
        cur.close()
        conn.close()
        
        if not results:
            last_results = None
            last_sql = None
            return "No results found"
        
        # Store for export/viz
        last_results = pd.DataFrame(results, columns=colnames)
        last_sql = sql
        
        return f"Query returned {len(results)} rows:\n{last_results.to_string()}"
    except Exception as e:
        return f"SQL Error: {str(e)}"

# Bind tools
llm_with_tools = llm.bind_tools([get_schema, execute_sql])

# Global conversation history
conversation_history = []

def run_agent(question):
    global conversation_history
    
    # Add user question to history
    conversation_history.append({"role": "user", "content": question})
    
    # Use FULL conversation history
    messages = conversation_history.copy()
    
    for iteration in range(5):
        response = llm_with_tools.invoke(messages)
        
        if response.tool_calls:
            tool_call = response.tool_calls[0]
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            print(f"[Step {iteration+1}] Using tool: {tool_name}")
            
            if tool_name == 'get_schema':
                result = get_schema.invoke(tool_args)
            elif tool_name == 'execute_sql':
                result = execute_sql.invoke(tool_args)
                print(f"SQL: {tool_args.get('sql', '')}")
            
            messages.append({"role": "assistant", "content": response.content, "tool_calls": response.tool_calls})
            messages.append({"role": "tool", "content": result, "tool_call_id": tool_call['id']})
        else:
            # Extract clean text from response
            if isinstance(response.content, list):
                clean_text = response.content[0].get('text', str(response.content[0]))
            else:
                clean_text = response.content
            
            # Save CLEAN TEXT to history (this fixes /history display)
            conversation_history.append({"role": "assistant", "content": clean_text})
            
            return clean_text
    
    return "Max iterations reached"

# Export function
def export_results(format='csv'):
    if last_results is None:
        print("❌ No results to export. Run a query first.")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == 'csv':
        filename = f"query_results_{timestamp}.csv"
        last_results.to_csv(filename, index=False)
        print(f"✅ Exported to {filename}")
    
    elif format == 'excel':
        filename = f"query_results_{timestamp}.xlsx"
        last_results.to_excel(filename, index=False)
        print(f"✅ Exported to {filename}")
    
    elif format == 'json':
        filename = f"query_results_{timestamp}.json"
        last_results.to_json(filename, orient='records', indent=2)
        print(f"✅ Exported to {filename}")

# Visualization function (FIXED)
def visualize_results():
    if last_results is None:
        print("❌ No results to visualize. Run a query first.")
        return
    
    import matplotlib.pyplot as plt
    
    # Auto-detect chart type
    if len(last_results.columns) == 2:
        df = last_results.copy()
        
        # Clean numeric column (remove $ and convert)
        col1, col2 = df.columns[0], df.columns[1]
        
        # Try to convert second column to numeric
        try:
            # Remove $ and commas, then convert
            if df[col2].dtype == 'object':  # String column
                df[col2] = df[col2].astype(str).str.replace('$', '').str.replace(',', '').astype(float)
        except:
            pass
        
        # Create bar chart
        plt.figure(figsize=(10, 6))
        df.plot(kind='bar', x=col1, y=col2, legend=False)
        plt.title('Query Results')
        plt.xlabel(col1)
        plt.ylabel(col2)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chart_{timestamp}.png"
        plt.savefig(filename)
        print(f"✅ Chart saved as {filename}")
        plt.show()
    else:
        print("❌ Visualization needs exactly 2 columns. Try: 'Show me X by Y'")

# Show history
def show_history():
    if not conversation_history:
        print("No conversation history yet.")
        return
    
    print("\n=== CONVERSATION HISTORY ===")
    for i, msg in enumerate(conversation_history):
        role = msg['role'].upper()
        content = msg['content']
        if isinstance(content, str):
            content = content[:100] + "..." if len(content) > 100 else content
        print(f"[{i+1}] {role}: {content}")
    print("============================\n")

# Clear history
def clear_history():
    global conversation_history
    conversation_history = []
    print("✅ Conversation history cleared")

# Interactive CLI
def main():
    print("=" * 60)
    print("TEXT-TO-SQL AGENT (Interactive Mode)")
    print("=" * 60)
    print("Commands:")
    print("  /export csv|excel|json  - Export last results")
    print("  /viz                    - Create chart from last results")
    print("  /history                - Show conversation history")
    print("  /clear                  - Clear conversation history")
    print("  /exit                   - Exit")
    print("=" * 60)
    print()
    
    while True:
        try:
            question = input("You: ").strip()
            
            if not question:
                continue
            
            # Handle commands
            if question == '/exit':
                print("Goodbye! 👋")
                break
            
            elif question.startswith('/export'):
                parts = question.split()
                format = parts[1] if len(parts) > 1 else 'csv'
                export_results(format)
            
            elif question == '/viz':
                visualize_results()
            
            elif question == '/history':
                show_history()
            
            elif question == '/clear':
                clear_history()
            
            else:
                # Regular query
                print("\nAI:", end=" ")
                result = run_agent(question)
                print(result)
                print()
        
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()