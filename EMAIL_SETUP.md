# Email Setup Guide

## 📧 Automatic Email Responses

The system now automatically sends email responses using the **agent's email** from the FreshDesk webhook data. No additional email configuration is required!

### How It Works

1. **FreshDesk webhook** includes agent information:
   - `agent_email`: The agent's email address
   - `agent_name`: The agent's name
2. **System automatically** uses agent's email to send responses
3. **Customer receives** email from the agent's address

### Optional SMTP Configuration

If you want to use a specific SMTP server, you can configure these optional environment variables:

```env
# Optional SMTP Configuration (uses agent's email by default)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

## 🚀 How It Works

1. **Customer sends inquiry** via FreshDesk
2. **FreshDesk webhook** includes agent information (`agent_email`, `agent_name`)
3. **Webhook triggers** the system
4. **AI processes** the customer query
5. **Response generated** in customer's language
6. **Email sent automatically** using agent's email address

## 📋 Email Template

The system sends emails with this format:

```
From: [Agent Name] <[Agent Email]>
To: [Customer Email]
Subject: Re: Your Support Request (Ticket #123)

Dear [Customer Name],

Thank you for contacting us. Here is the information you requested:

[AI Response in customer's language]

If you have any further questions or need additional assistance, please don't hesitate to reach out to us.

Best regards,
[Agent Name]
Customer Support Team
```

## ✅ Testing

To test the email functionality:

1. **Start the server**: `python api.py`
2. **Send a test webhook** to `/webhook/freshdesk` with agent information:
   ```json
   {
     "freshdesk_webhook": {
       "ticket_id": "123",
       "ticket_contact_email": "customer@example.com",
       "ticket_contact_name": "John Doe",
       "ticket_subject": "Order inquiry",
       "ticket_description": "What is my order status?",
       "agent_email": "agent@company.com",
       "agent_name": "Support Agent"
     }
   }
   ```
3. **Check the console logs** for email status
4. **Verify email delivery** in customer's inbox

## 🔧 Troubleshooting

### Common Issues

1. **"Agent email not provided"**
   - Ensure FreshDesk webhook includes `agent_email` field
   - Check webhook data structure

2. **"Authentication required"**
   - Some SMTP servers require authentication
   - Configure SMTP credentials if needed

3. **"Connection refused"**
   - Check SMTP server and port settings
   - Verify firewall/network access

### Debug Mode

The system will log email sending status:
- ✅ Email sent successfully!
- ❌ Failed to send email
- ⚠️ Authentication required

Check the console output for detailed error messages.
