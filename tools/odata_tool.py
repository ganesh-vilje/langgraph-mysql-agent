import os
import requests
import json
from langchain.tools import tool
from dotenv import load_dotenv
from urllib.parse import quote

# Load environment variables
load_dotenv()

# Dynamics NAV OData configuration
ODATA_CONFIG = {
    "base_url": os.getenv("DYNAMICS_NAV_BASE_URL"),  # e.g., "https://your-nav-server:7048/BC140/ODataV4"
    "username": os.getenv("DYNAMICS_NAV_USERNAME"),
    "password": os.getenv("DYNAMICS_NAV_PASSWORD"),
    # "company": os.getenv("DYNAMICS_NAV_COMPANY", "CRONUS")  # Default company
}

def get_auth_headers():
    """Get authentication headers for Dynamics NAV OData API"""
    if ODATA_CONFIG["username"] and ODATA_CONFIG["password"]:
        import base64
        credentials = f"{ODATA_CONFIG['username']}:{ODATA_CONFIG['password']}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    return {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def run_odata_query(entity_name: str, filters: str = "", select: str = "", top: int = 100):
    """Run an OData query against Dynamics NAV and return results."""
    try:
        base_url = ODATA_CONFIG["base_url"]
        if not base_url:
            return {"error": "Dynamics NAV base URL not configured in .env file"}
        
        # Handle different entity name mappings for this specific NAV system
        entity_mapping = {
            "SalesHeaders": "SalesList",  # Based on the error, SalesHeaders maps to SalesList
            "SalesLines": "SalesList",    # Sales lines might also be in SalesList
            "Customers": "Customers",
            "Items": "Items",
            "Vendors": "Vendors"
        }
        
        # Get the correct entity name
        actual_entity = entity_mapping.get(entity_name, entity_name)
        
        # Build the OData URL - handle case where base_url already includes the entity
        if base_url.endswith(f'/{actual_entity}'):
            url = base_url
        else:
            url = f"{base_url}/{actual_entity}"
        
        # Add query parameters
        params = []
        if select:
            params.append(f"$select={select}")
        if filters:
            params.append(f"$filter={filters}")
        if top:
            params.append(f"$top={top}")
        
        if params:
            url += "?" + "&".join(params)
        
        # Debug: Print the URL being called (remove in production)
        print(f"🔗 OData URL: {url}", flush=True)
        
        # Make the request
        headers = get_auth_headers()
        response = requests.get(url, headers=headers, timeout=30)
        
        # Debug: Print response details
        print(f"📊 Response Status: {response.status_code}", flush=True)
        if response.status_code != 200:
            print(f"❌ Response Text: {response.text[:500]}", flush=True)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("value", [])
            print(f"✅ Found {len(results)} records", flush=True)
            return {"results": results}
        else:
            return {"error": f"OData request failed with status {response.status_code}: {response.text[:500]}"}
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}", flush=True)
        return {"error": f"Error executing OData query: {str(e)}"}

@tool
def query_odata(entity_name: str, filters: str = "", select: str = "", top: int = 100):
    """
    Execute an OData query against Microsoft Dynamics NAV.
    
    Args:
        entity_name: The OData entity name (e.g., 'Customers', 'Items', 'SalesHeaders')
        filters: OData filter expression (e.g., "No eq 'CUST001'")
        select: Comma-separated list of fields to select (e.g., "No,Name,Address")
        top: Maximum number of records to return (default: 100)
    
    Returns:
        Dictionary with query results or error message
    """
    return run_odata_query(entity_name, filters, select, top)

@tool
def get_odata_schema():
    """
    Get the available OData entities and their structure from Dynamics NAV.
    This returns a list of available entities that can be queried.
    """
    try:
        base_url = ODATA_CONFIG["base_url"]
        if not base_url:
            return {"error": "Dynamics NAV base URL not configured"}
        
        # Get the service document to see available entities
        url = f"{base_url}/$metadata"
        headers = get_auth_headers()
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # For now, return a basic list of common Dynamics NAV entities
            # In a real implementation, you'd parse the $metadata XML
            common_entities = {
                "entities": [
                    {"name": "Customers", "description": "Customer master data"},
                    {"name": "Items", "description": "Item master data"},
                    {"name": "SalesList", "description": "Sales orders (headers and lines combined)"},
                    {"name": "SalesHeaders", "description": "Sales order headers (maps to SalesList)"},
                    {"name": "SalesLines", "description": "Sales order lines (maps to SalesList)"},
                    {"name": "PurchaseHeaders", "description": "Purchase order headers"},
                    {"name": "PurchaseLines", "description": "Purchase order lines"},
                    {"name": "Vendors", "description": "Vendor master data"},
                    {"name": "Employees", "description": "Employee master data"},
                    {"name": "GLAccounts", "description": "General Ledger accounts"},
                    {"name": "GLBudgets", "description": "General Ledger budgets"}
                ]
            }
            return common_entities
        else:
            return {"error": f"Failed to get schema: {response.status_code}"}
            
    except Exception as e:
        return {"error": f"Error getting OData schema: {str(e)}"}

@tool
def search_odata_data(query: str, entity_name: str = "Customers"):
    """
    Search for data in Dynamics NAV using natural language query.
    
    Args:
        query: Natural language search query (e.g., "customer with name John")
        entity_name: The entity to search in (default: Customers)
    
    Returns:
        Dictionary with search results
    """
    try:
        # Clean the query - remove extra spaces and handle order numbers
        clean_query = query.strip().replace("  ", " ")
        
        # Handle order number searches specifically
        if "order" in clean_query.lower() and any(char.isdigit() for char in clean_query):
            # Extract order number from query like "order OF0000001" or "OF0000001"
            import re
            order_match = re.search(r'([A-Z]{2}\d+)', clean_query.upper())
            if order_match:
                order_number = order_match.group(1)
                # Search for exact order number match
                filters = f"No eq '{order_number}'"
                return run_odata_query("SalesHeaders", filters, top=50)
        
        # This is a simplified search - in practice, you might want to use
        # Dynamics NAV's search capabilities or implement more sophisticated filtering
        
        # For now, we'll do a basic search on common fields
        if entity_name.lower() == "customers":
            # Search in customer name, number, or address
            filters = f"contains(tolower(Name), tolower('{clean_query}')) or contains(tolower(No), tolower('{clean_query}'))"
        elif entity_name.lower() == "items":
            # Search in item description or number
            filters = f"contains(tolower(Description), tolower('{clean_query}')) or contains(tolower(No), tolower('{clean_query}'))"
        elif entity_name.lower() in ["salesheaders", "saleslist"]:
            # Search in sales order number or customer
            filters = f"contains(tolower(No), tolower('{clean_query}')) or contains(tolower(Sell_to_Customer_No), tolower('{clean_query}'))"
        else:
            # Generic search - try to find the query in any text field
            filters = f"contains(tolower(No), tolower('{clean_query}'))"
        
        return run_odata_query(entity_name, filters, top=50)
        
    except Exception as e:
        return {"error": f"Error searching OData: {str(e)}"}
