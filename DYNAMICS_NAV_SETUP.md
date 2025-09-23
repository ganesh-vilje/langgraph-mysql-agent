# Microsoft Dynamics NAV OData Integration Setup

## Environment Variables Required

Add these variables to your `.env` file:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Microsoft Dynamics NAV OData Configuration
DYNAMICS_NAV_BASE_URL=https://your-nav-server:7048/BC140/ODataV4
DYNAMICS_NAV_USERNAME=your_username
DYNAMICS_NAV_PASSWORD=your_password
DYNAMICS_NAV_COMPANY=CRONUS
```

## Example Configurations

### Business Central On-Premises
```env
DYNAMICS_NAV_BASE_URL=https://your-server:7048/BC140/ODataV4
```

### Business Central Online
```env
DYNAMICS_NAV_BASE_URL=https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/ODataV4
```

### Older NAV Versions
```env
DYNAMICS_NAV_BASE_URL=https://your-server:7048/NAV/ODataV4
```

## Common OData Entities

The system can query these common Dynamics NAV entities:
- **Customers** - Customer master data
- **Items** - Item master data  
- **SalesHeaders** - Sales order headers
- **SalesLines** - Sales order lines
- **PurchaseHeaders** - Purchase order headers
- **PurchaseLines** - Purchase order lines
- **Vendors** - Vendor master data
- **Employees** - Employee master data
- **GLAccounts** - General Ledger accounts
- **GLBudgets** - General Ledger budgets

## Testing the Integration

1. Start the FastAPI server: `python -m uvicorn api:app --reload`
2. Test with a sample query: `python main.py`
3. Try queries like:
   - "Show me all customers"
   - "Find customer with name John"
   - "What items do we have in stock?"
   - "Show sales orders for customer CUST001"

