from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from dotenv import load_dotenv
import psycopg2
import os

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
    if not sql.strip().upper().startswith('SELECT'):
        return "Error: Only SELECT queries allowed"
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(sql)
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        if not results:
            return "No results found"
        
        return f"Query returned {len(results)} rows. First result: {results[0]}"
    except Exception as e:
        return f"SQL Error: {str(e)}"

# Bind tools
llm_with_tools = llm.bind_tools([get_schema, execute_sql])

# Agent loop
# Global conversation history (simulating memory)
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
                print(f"SQL executed: {tool_args.get('sql', '')[:100]}...")
            
            messages.append({"role": "assistant", "content": response.content, "tool_calls": response.tool_calls})
            messages.append({"role": "tool", "content": result, "tool_call_id": tool_call['id']})
        else:
            # Save assistant response to history
            conversation_history.append({"role": "assistant", "content": response.content})
            
            if isinstance(response.content, list):
                return response.content[0]['text']
            return response.content
    
    return "Max iterations reached"

# Test
print("Text-to-SQL Agent with LangChain!\n")
question = "How many customers do we have?"
print(f"Q: {question}")
answer = run_agent(question)
print(f"\nA: {answer}\n")
# Test memory issue
print("\n--- Testing follow-up (no memory yet) ---")
question2 = "How many are from California?"
print(f"Q: {question2}")
answer2 = run_agent(question2)
print(f"A: {answer2}")
# Real memory test
print("\n--- Real memory test ---")
question3 = "Show me total sales by state"
print(f"Q: {question3}")
answer3 = run_agent(question3)
print(f"A: {answer3}\n")

question4 = "Now show just the top 3"
print(f"Q: {question4}")
answer4 = run_agent(question4)
print(f"A: {answer4}")