import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
from agent.react_agent import get_react_agent
import logging

logger = logging.getLogger(__name__)

class EmailAgent:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.agent = get_react_agent(user_id=f"email_{email}")
    
    def read_emails(self, folder: str = "INBOX"):
        """Read unread emails."""
        try:
            imap = imaplib.IMAP4_SSL("imap.gmail.com")
            imap.login(self.email, self.password)
            imap.select(folder)
            
            # Get unread emails
            _, data = imap.search(None, "UNSEEN")
            email_ids = data[0].split()
            
            emails = []
            for email_id in email_ids[:10]:  # Last 10
                _, msg_data = imap.fetch(email_id, "(RFC822)")
                from email import message_from_bytes
                msg = message_from_bytes(msg_data[0][1])
                
                emails.append({
                    "from": msg["From"],
                    "subject": msg["Subject"],
                    "body": msg.get_payload(decode=True).decode("utf-8")
                })
            
            imap.close()
            return emails
        
        except Exception as e:
            logger.error(f"Error reading emails: {e}")
            return []
    
    def send_email(self, to: str, subject: str, body: str):
        """Send email response."""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email
            msg["To"] = to
            msg["Subject"] = subject
            
            msg.attach(MIMEText(body, "plain"))
            
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent to {to}")
        
        except Exception as e:
            logger.error(f"Error sending email: {e}")
    
    def process_emails(self):
        """Read and respond to emails."""
        emails = self.read_emails()
        
        for email in emails:
            try:
                # Process with agent
                response, _ = self.agent.process_input(email["body"])
                
                # Send response
                self.send_email(
                    to=email["from"],
                    subject=f"Re: {email['subject']}",
                    body=response
                )
            
            except Exception as e:
                logger.error(f"Error processing email: {e}")

# Usage
if __name__ == "__main__":
    agent = EmailAgent("support@example.com", "app_password")
    agent.process_emails()