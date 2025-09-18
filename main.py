import os
from dotenv import load_dotenv
from agent.agent import build_agent

# Load env vars
load_dotenv()

SYSTEM_PROMPT = (
    "You are an assistant that helps users query a MySQL database.\n"
    "You have access to two tools:\n"
    "1. `get_schema` - to get the database schema (tables and columns)\n"
    "2. `query_mysql` - to execute SQL queries\n"
    "\n"
    "Process user queries by:\n"
    "1. If you need to understand the database structure, call `get_schema` first\n"
    "2. Generate a valid MySQL SQL query based on the user's request\n"
    "3. Use `query_mysql` to execute the query\n"
    "4. Present the results in a clear, readable format\n"
    "\n"
    "Always use the tools to get actual data. Do not make up or guess database content.\n"
    "If you don't know the schema, call get_schema first."
)

def main():
    agent = build_agent()

    print("🚀 LangGraph + MySQL Agent (Natural Language → SQL, Schema-Aware)")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye 👋")
            break

        response = agent.invoke(
            {
                "messages": [
                    ("system", SYSTEM_PROMPT),
                    ("user", user_input)
                ]
            },
            config={"recursion_limit": 50}  # default was 25
        )

        print("Agent:", response["messages"][-1].content)

if __name__ == "__main__":
    main()
