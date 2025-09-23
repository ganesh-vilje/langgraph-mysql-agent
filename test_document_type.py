#!/usr/bin/env python3
"""
Test script to demonstrate document type handling in the LangGraph MySQL Agent.
This script shows how the enhanced system now handles document type queries.
"""

import os
from dotenv import load_dotenv
from agent.agent import build_agent

# Load env vars
load_dotenv()

def test_document_type_queries():
    """Test various document type queries to demonstrate the enhanced functionality."""
    
    agent = build_agent()
    
    # Test queries that should now work with document type handling
    test_queries = [
        "What type of document is order OF0000001?",
        "Show me all invoices",
        "List all quotes",
        "Find all orders for customer CUST001",
        "Is order OF0000002 an invoice or a quote?",
        "Show me all credit memos",
        "What document types are available?",
        "Get all documents of type Order"
    ]
    
    print("🧪 Testing Document Type Queries")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 40)
        
        try:
            response = agent.invoke({
                "messages": [
                    ("system", "You are an intelligent assistant that helps users query Microsoft Dynamics NAV via OData API. You have access to four tools: 1. get_odata_schema - to get available Dynamics NAV entities, 2. query_odata - to execute OData queries, 3. search_odata_data - to search for data using natural language, 4. query_by_document_type - to query data by specific document type (Quote, Order, Invoice, etc.). Always understand the user's intent and provide helpful responses. When users ask about document types, always include Document_Type field in your queries and explain document types in user-friendly terms."),
                    ("user", query)
                ]
            }, config={"recursion_limit": 50})
            
            print(f"Response: {response['messages'][-1].content}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("-" * 40)

if __name__ == "__main__":
    test_document_type_queries()
