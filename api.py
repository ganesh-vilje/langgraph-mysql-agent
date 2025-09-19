import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from agent.agent import build_agent

# Load env vars
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="LangGraph + MySQL Agent API with Email Support")

# Build agent once
agent = build_agent()

# System prompt for customer support
SYSTEM_PROMPT = (
    "You are a customer support assistant. When you receive a customer query, use the available tools to:\n"
    "1. Get database schema if needed\n"
    "2. Query the database for the answer\n"
    "3. Provide a clear, helpful response\n"
    "Always provide accurate information based on the database content."
)

class QueryRequest(BaseModel):
    query: str


@app.get("/")
def root():
    return {"message": "LangGraph + MySQL Agent API with Email Support is running 🚀"}

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

@app.post("/webhook/freshdesk")
def handle_freshdesk_webhook(request: dict):
    """Handle FreshDesk webhook and process customer query"""
    try:
        # Debug: Print the raw request to see what FreshDesk is sending
        print("\n" + "="*80)
        print("🔍 RAW WEBHOOK DATA:")
        print("="*80)
        print(json.dumps(request, indent=2))
        print("="*80)
        
        # Extract data from FreshDesk webhook
        webhook_data = request.get("freshdesk_webhook", {})
        ticket_id = webhook_data.get("ticket_id")
        customer_email = webhook_data.get("ticket_contact_email")
        customer_name = webhook_data.get("ticket_contact_name", "Customer")
        subject = webhook_data.get("ticket_subject", "")
        description = webhook_data.get("ticket_description", "")
        
        # Clean HTML from description
        import re
        description = re.sub(r'<[^>]+>', '', description)  # Remove HTML tags
        description = description.strip()
        
        # Console log ticket details
        print("🎫 EXTRACTED TICKET DETAILS:")
        print("="*80)
        print(f"Ticket ID: {ticket_id}")
        print(f"Customer: {customer_name}")
        print(f"Email: {customer_email}")
        print(f"Subject: {subject}")
        print(f"Description: {description}")
        print("-"*80)
        
        # Process the customer query (include subject for order IDs and other important info)
        full_query = f"Subject: {subject}\nDescription: {description}"
        
        # Process the customer query
        response = agent.invoke({
            "messages": [
                ("system", SYSTEM_PROMPT),
                ("user", f"Customer: {customer_name}, Email: {customer_email}, Query: {full_query}")
            ]
        })
        
        # Get the agent's response
        agent_response = response["messages"][-1].content
        
        # Console log the response
        print("🤖 AGENT RESPONSE:")
        print("-"*80)
        print(agent_response)
        print("="*80)
        print("✅ Response processed successfully!")
        print("="*80 + "\n")
        
        return {
            "status": "success",
            "message": "Query processed successfully",
            "ticket_id": ticket_id,
            "customer_email": customer_email,
            "response": agent_response
        }
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")
