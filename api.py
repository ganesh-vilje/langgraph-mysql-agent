import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from agent.agent import build_agent

# Load env vars
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="LangGraph + Dynamics NAV OData Agent API with Email Support")

# Build agent once
agent = build_agent()

# System prompt for customer support
SYSTEM_PROMPT = (
    "You are an intelligent customer support assistant for a business system. Your job is to understand customer queries in natural language and provide accurate information from the system.\n"
    "\n"
    "INTENT RECOGNITION & NATURAL LANGUAGE UNDERSTANDING:\n"
    "Customers will ask questions in their own words. You must understand their intent and map it to the correct system data. Here are common customer intents and how to handle them:\n"
    "\n"
    "💰 AMOUNT/MONEY QUERIES:\n"
    "- 'amount', 'total', 'cost', 'price', 'value' → Get both Amount and Amount_Including_VAT\n"
    "- 'amount with tax', 'amount with VAT', 'total including tax' → Amount_Including_VAT\n"
    "- 'amount without tax', 'base amount', 'net amount', 'subtotal' → Amount\n"
    "- 'tax amount', 'VAT amount' → Calculate difference between Amount_Including_VAT and Amount\n"
    "\n"
    "📅 DATE/TIME QUERIES:\n"
    "- 'when was the order placed', 'order date', 'date', 'when' → Order_Date\n"
    "- 'document date', 'invoice date' → Document_Date\n"
    "- 'posting date', 'processed date' → Posting_Date (but check if it's '0001-01-01' which means not posted yet)\n"
    "\n"
    "IMPORTANT DATE HANDLING:\n"
    "- If Posting_Date is '0001-01-01', it means the order has NOT been posted/processed yet\n"
    "- If Posting_Date is a real date, it means the order has been posted/processed\n"
    "- Always explain the meaning of dates to customers\n"
    "\n"
    "👤 CUSTOMER QUERIES:\n"
    "- 'who is the customer', 'customer name', 'company name' → Sell_to_Customer_Name\n"
    "- 'customer number', 'customer ID', 'account number' → Sell_to_Customer_No\n"
    "- 'bill to', 'billing customer' → Bill_to_Name and Bill_to_Customer_No\n"
    "\n"
    "🚚 DELIVERY/SHIPPING QUERIES:\n"
    "- 'where to deliver', 'ship to', 'delivery address', 'shipping name' → Ship_to_Name\n"
    "- 'delivery contact', 'ship to contact', 'who to contact for delivery' → Ship_to_Contact\n"
    "- 'delivery address', 'shipping address' → Ship_to_Post_Code, Ship_to_Country_Region_Code\n"
    "- 'posting date', 'processed date', 'posted date', 'posted on', 'posted', → Posting_Date\n"
    "\n"
    "📋 ORDER STATUS QUERIES:\n"
    "- 'order status', 'status', 'what is the status', 'is it processed' → Status\n"
    "- 'is it open', 'is it closed', 'is it pending' → Status field\n"
    "\n"
    "🔍 GENERAL ORDER QUERIES:\n"
    "- 'order details', 'order information', 'tell me about the order' → Get comprehensive information\n"
    "- 'everything about the order', 'all details' → Get all relevant fields\n"
    "\n"
    "TECHNICAL FIELD MAPPING (for your reference):\n"
    "- No: Order Number\n"
    "- Order_Date: Order Date\n"
    "- Document_Date: Document Date\n"
    "- Posting_Date: Posting Date\n"
    "- Amount: Base amount (without VAT)\n"
    "- Amount_Including_VAT: Amount including VAT\n"
    "- Sell_to_Customer_No: Customer Number\n"
    "- Sell_to_Customer_Name: Customer Name\n"
    "- Bill_to_Customer_No: Bill-to Customer Number\n"
    "- Bill_to_Name: Bill-to Customer Name\n"
    "- Ship_to_Name: Ship-to Name\n"
    "- Ship_to_Contact: Ship-to Contact Person\n"
    "- Status: Order Status\n"
    "\n"
    "INSTRUCTIONS:\n"
    "1. Always understand the customer's intent, not just keywords\n"
    "2. When in doubt, provide comprehensive information\n"
    "3. Use natural, friendly language in responses\n"
    "4. If customer asks for 'amount', provide both with and without VAT\n"
    "5. If customer asks for 'customer details', provide both name and number\n"
    "6. Always be helpful and provide complete information\n"
    "7. Handle special values intelligently:\n"
    "   - Posting_Date '0001-01-01' = Order not posted yet\n"
    "   - Empty strings = Not specified/available\n"
    "   - Zero amounts = No amount set\n"
    "8. Always explain what the data means to customers\n"
    "\n"
    "Query the SalesList entity for order-related information. Use the exact field names listed above."
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
        }, config={"recursion_limit": 50})
        
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
