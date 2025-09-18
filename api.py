import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from agent.agent import build_agent

# Load env vars
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="LangGraph + MySQL Agent API")

# Build agent once
agent = build_agent()

# System prompt (same as CLI)
SYSTEM_PROMPT = (
    "You are an assistant that helps users query a MySQL database.\n"
    "1. First, if needed, use the `get_schema` tool to understand tables and columns.\n"
    "2. Then, generate a valid MySQL SQL query.\n"
    "3. Use `query_mysql` to run the query.\n"
    "4. Return a clean, human-readable answer with the results.\n"
    "Do NOT invent tables or columns that don’t exist in the schema."
)

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def root():
    return {"message": "LangGraph + MySQL Agent API is running 🚀"}

@app.post("/query")
def run_query(request: QueryRequest):
    """Accept a natural language query and return the agent's response."""
    response = agent.invoke({
        "messages": [
            ("system", SYSTEM_PROMPT),
            ("user", request.query)
        ]
    })

    raw_output = response["messages"][-1].content

    # Try parsing as JSON (if tool returned JSON string)
    try:
        parsed_output = json.loads(raw_output)
        return parsed_output
    except Exception:
        return {"response": raw_output}
