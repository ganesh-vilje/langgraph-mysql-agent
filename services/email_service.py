import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
    
    def send_customer_response(self, customer_email: str, customer_name: str, agent_response: str, agent_email: str, agent_name: str, ticket_id: str = None):
        """
        Send response email to customer using agent's email
        """
        try:
            if not agent_email:
                print("❌ Agent email not provided. Cannot send email.")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{agent_name} <{agent_email}>"
            msg['To'] = customer_email
            msg['Subject'] = f"Re: Your Support Request" + (f" (Ticket #{ticket_id})" if ticket_id else "")
            
            # Create email body
            body = f"""
Dear {customer_name},

Thank you for contacting us. Here is the information you requested:

{agent_response}

If you have any further questions or need additional assistance, please don't hesitate to reach out to us.

Best regards,
{agent_name}
Customer Support Team
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email using agent's email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                # Try to send without authentication first (some SMTP servers allow this)
                try:
                    text = msg.as_string()
                    server.sendmail(agent_email, customer_email, text)
                except Exception as auth_error:
                    print(f"⚠️ Authentication required. Please configure SMTP credentials for {agent_email}")
                    print(f"Error: {str(auth_error)}")
                    return False
            
            print(f"✅ Email sent successfully to {customer_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            return False

# Create global instance
email_service = EmailService()
