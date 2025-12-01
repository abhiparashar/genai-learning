from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

# Load API key
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

# Initialize LangChain's Gemini wrapper
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    temperature=0.7
)

# Create a simple prompt with message history
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# Create chain
chain = prompt | llm

# Store for message history
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Wrap chain with message history
conversation = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# Have a conversation
print("\n--- Conversation with Memory ---")
response1 = conversation.invoke(
    {"input": "My name is Raj"},
    config={"configurable": {"session_id": "abc123"}}
)
print(response1.content)

response2 = conversation.invoke(
    {"input": "What's my name?"},
    config={"configurable": {"session_id": "abc123"}}
)
print(response2.content)

response3 = conversation.invoke(
    {"input": "What did we talk about?"},
    config={"configurable": {"session_id": "abc123"}}
)
print(response3.content)

# Let's see what's stored in memory
print("\n--- What's in Memory ---")
print(f"Session ID: abc123")
print(f"Number of messages: {len(store['abc123'].messages)}")
print("\nActual messages:")
for i, msg in enumerate(store['abc123'].messages):
    print(f"{i+1}. {msg.type}: {msg.content}")