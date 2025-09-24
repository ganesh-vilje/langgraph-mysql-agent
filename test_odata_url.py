#!/usr/bin/env python3
"""
Test script to debug OData URL construction
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_url_construction():
    """Test how the OData URL is being constructed"""
    print("🔍 Testing OData URL Construction")
    print("="*50)
    
    # Get the base URL from environment
    base_url = os.getenv("DYNAMICS_NAV_BASE_URL")
    print(f"Base URL from .env: {base_url}")
    
    # Test entity mapping
    entity_mapping = {
        "SalesHeaders": "SalesList",
        "SalesLines": "SalesList", 
        "SalesList": "SalesList",
        "SalesOrder": "SalesOrder",
        "Customers": "Customers",
        "Items": "Items",
        "Vendors": "Vendors"
    }
    
    # Test different entity names
    test_entities = ["SalesList", "SalesOrder", "SalesHeaders"]
    
    for entity_name in test_entities:
        actual_entity = entity_mapping.get(entity_name, entity_name)
        base_url_clean = base_url.rstrip('/') if base_url else ""
        url = f"{base_url_clean}/{actual_entity}"
        
        print(f"\nEntity: '{entity_name}' -> '{actual_entity}'")
        print(f"URL: {url}")
    
    # Test with query parameters
    print(f"\n📋 Full URL with query parameters:")
    entity_name = "SalesList"
    actual_entity = entity_mapping.get(entity_name, entity_name)
    base_url_clean = base_url.rstrip('/') if base_url else ""
    url = f"{base_url_clean}/{actual_entity}"
    
    # Add query parameters like in the error
    params = [
        "$select=Order_Date,Document_Date",
        "$filter=No eq '10000000352'",
        "$top=100"
    ]
    full_url = url + "?" + "&".join(params)
    
    print(f"Full URL: {full_url}")

if __name__ == "__main__":
    test_url_construction()

