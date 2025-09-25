import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from agent.agent import build_agent
from services.email_service import email_service

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
    "🚨 CRITICAL LANGUAGE RULE: 🚨\n"
    "BEFORE responding, you MUST identify the language of the customer's input.\n"
    "If the customer writes in English, you MUST respond in English.\n"
    "If the customer writes in Spanish, you MUST respond in Spanish.\n"
    "If the customer writes in French, you MUST respond in French.\n"
    "If the customer writes in German, you MUST respond in German.\n"
    "If the customer writes in Swedish, you MUST respond in Swedish.\n"
    "If the customer writes in Italian, you MUST respond in Italian.\n"
    "If the customer writes in Portuguese, you MUST respond in Portuguese.\n"
    "If the customer writes in Dutch, you MUST respond in Dutch.\n"
    "If the customer writes in ANY language, you MUST respond in that EXACT SAME language.\n"
    "NEVER translate the customer's language to a different language.\n"
    "\n"
    "EXAMPLES:\n"
    "- Customer input: 'what is the shipment date' (English) → Response: 'The shipment date is...' (English)\n"
    "- Customer input: '¿cuál es la fecha de envío' (Spanish) → Response: 'La fecha de envío es...' (Spanish)\n"
    "- Customer input: 'quelle est la date d'expédition' (French) → Response: 'La date d'expédition est...' (French)\n"
    "- Customer input: 'wann ist das Versanddatum' (German) → Response: 'Das Versanddatum ist...' (German)\n"
    "- Customer input: 'Ge mig alla orderuppgifter' (Swedish) → Response: 'Här är alla orderuppgifter...' (Swedish)\n"
    "- Customer input: 'dammi tutti i dettagli dell'ordine' (Italian) → Response: 'Ecco tutti i dettagli dell'ordine...' (Italian)\n"
    "\n"
    "REMEMBER: Match the input language exactly. English input = English output. Swedish input = Swedish output.\n"
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
    "- 'order date', 'order date', 'date', 'when' → Order_Date\n"
    "- 'what is the order date', 'what is the date', 'what is the when' → Order_Date\n"
    "- 'document date', 'invoice date' → Document_Date\n"
    "- 'what is the document date', 'what is the invoice date' → Document_Date\n"
    "- 'posting date', 'processed date' → Posting_Date (but check if it's '0001-01-01' which means not posted yet)\n"
    "- 'what is the posting date', 'what is the processed date' → Posting_Date (but check if it's '0001-01-01' which means not posted yet)\n"
    "\n"
    "- 'due date', 'due date', 'date', 'when' → Due_Date\n"
    "- 'what is the due date', 'what is the date', 'what is the when' → Due_Date\n"
    "IMPORTANT DATE HANDLING:\n"
    "- If Posting_Date is '0001-01-01', it means the order has NOT been posted/processed yet\n"
    "- If Posting_Date is a real date, it means the order has been posted/processed\n"
    "- Always explain the meaning of dates to customers\n"
    "\n"
    "👤 CUSTOMER QUERIES:\n"
    "- 'who is the customer', 'customer name', 'company name' → Sell_to_Customer_Name\n"
    "- 'customer number', 'customer ID', 'account number' → Sell_to_Customer_No\n"
    "- 'bill to', 'billing customer' → Bill_to_Name and Bill_to_Customer_No\n"
    "- 'billing address', 'billing customer address' → Bill_to_Address\n"
    "- 'billing city', 'billing customer city' → Bill_to_City\n"
    "- 'billing state', 'billing customer state' → Bill_to_State\n"
    "- 'billing country', 'billing customer country' → Bill_to_Country_Region_Code\n"
    "- 'billing postal code', 'billing customer postal code' → Bill_to_Post_Code\n"
    "\n"
    "🚚 DELIVERY/SHIPPING QUERIES:\n"
    "- 'where to deliver', 'ship to', 'delivery address', 'shipping name' → Ship_to_Name\n"
    "- 'delivery contact', 'ship to contact', 'who to contact for delivery' → Ship_to_Contact\n"
    "- 'delivery address', 'shipping address' → Ship_to_Post_Code, Ship_to_Country_Region_Code\n"
    "- 'shipment date', 'shipping date', 'delivery date', 'when will it ship', 'when is it shipped' → Shipment_Date\n"
    "- 'requested delivery date', 'delivery requested date' → Requested_Delivery_Date\n"
    "- 'promised delivery date', 'promised date' → Promised_Delivery_Date\n"
    "- 'posting date', 'processed date', 'posted date', 'posted on', 'posted' → Posting_Date\n"
    "\n"
    "📋 ORDER STATUS QUERIES:\n"
    "- 'order status', 'status', 'what is the status', 'is it processed' → Status\n"
    "- 'is it open', 'is it closed', 'is it pending' → Status field\n"
    "\n"
    "🔍 GENERAL ORDER QUERIES:\n"
    "- 'order details', 'order information', 'tell me about the order' → Get comprehensive information\n"
    "- 'everything about the order', 'all details' → Get all relevant fields\n"
    "- 'phone number', 'contact number', 'contact phone number' → Phone_No\n"
    "- 'what is the phone number', 'what is the contact number', 'what is the contact phone number' → Phone_No\n"
    "- 'email address', 'contact email address' → E_Mail\n"
    "- 'contact person', 'contact name' → Contact_Person\n"
    "- 'shipping address', 'shipping customer address' → Ship_to_Address\n"
    "- 'shipping city', 'shipping customer city' → Ship_to_City\n"
    "- 'shipping state', 'shipping customer state' → Ship_to_State\n"
    "- 'shipping country', 'shipping customer country' → Ship_to_Country_Region_Code\n"
    "\n"
    "TECHNICAL FIELD MAPPING (for your reference):\n"
    "- No: Order Number\n"
    "- Order_Date: Order Date\n"
    "- Document_Date: Document Date\n"
    "- Posting_Date: Posting Date\n"
    "- Shipment_Date: Shipment Date (when the order was/will be shipped)\n"
    "- Requested_Delivery_Date: Requested Delivery Date\n"
    "- Promised_Delivery_Date: Promised Delivery Date\n"
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
    "1. 🚨 FIRST AND MOST IMPORTANT: Identify the language of the customer's input and respond in that EXACT SAME language\n"
    "2. If customer input is in English, respond in English\n"
    "3. If customer input is in Spanish, respond in Spanish\n"
    "4. If customer input is in French, respond in French\n"
    "5. If customer input is in German, respond in German\n"
    "6. If customer input is in Swedish, respond in Swedish\n"
    "7. If customer input is in Italian, respond in Italian\n"
    "8. If customer input is in Portuguese, respond in Portuguese\n"
    "9. If customer input is in Dutch, respond in Dutch\n"
    "10. If customer input is in ANY language, respond in that EXACT SAME language\n"
    "11. NEVER translate to a different language than the input\n"
    "12. Use proper sentence formation and formatting for that language\n"
    "13. Always understand the customer's intent, not just keywords\n"
    "14. When in doubt, provide comprehensive information\n"
    "15. Use natural, friendly language in responses\n"
    "16. If customer asks for 'amount', provide both with and without VAT\n"
    "17. If customer asks for 'customer details', provide both name and number\n"
    "18. Always be helpful and provide complete information\n"
    "19. Handle special values intelligently:\n"
    "   - Posting_Date '0001-01-01' = Order not posted yet\n"
    "   - Empty strings = Not specified/available\n"
    "   - Zero amounts = No amount set\n"
    "20. Always explain what the data means to customers\n"
    "21. Maintain professional tone while being conversational\n"
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
        
        # Extract agent information from webhook
        agent_email = webhook_data.get("agent_email")
        agent_name = webhook_data.get("agent_name", "Support Agent")
        
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
        
        # Send email response to customer
        print("📧 SENDING EMAIL RESPONSE:")
        print("-"*80)
        print(f"Agent Email: {agent_email}")
        print(f"Agent Name: {agent_name}")
        print(f"Customer Email: {customer_email}")
        print("-"*80)
        
        email_sent = email_service.send_customer_response(
            customer_email=customer_email,
            customer_name=customer_name,
            agent_response=agent_response,
            agent_email=agent_email,
            agent_name=agent_name,
            ticket_id=ticket_id
        )
        
        if email_sent:
            print("✅ Email sent successfully!")
        else:
            print("❌ Failed to send email")
        
        print("="*80)
        print("✅ Response processed successfully!")
        print("="*80 + "\n")
        
        return {
            "status": "success",
            "message": "Query processed successfully",
            "ticket_id": ticket_id,
            "customer_email": customer_email,
            "response": agent_response,
            "email_sent": email_sent
        }
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")
