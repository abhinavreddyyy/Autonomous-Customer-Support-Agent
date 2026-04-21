from simple_salesforce import Salesforce
from agent.react_agent import get_react_agent
import logging

logger = logging.getLogger(__name__)

class SalesforceIntegration:
    def __init__(self, username: str, password: str, security_token: str):
        self.sf = Salesforce(
            username=username,
            password=password,
            security_token=security_token
        )
        self.agent = get_react_agent(user_id="salesforce")
    
    def get_customer_data(self, customer_id: str):
        """Get customer info from Salesforce."""
        try:
            result = self.sf.query(
                f"SELECT Id, Name, Email, Industry FROM Account WHERE Id = '{customer_id}'"
            )
            return result["records"][0] if result["records"] else None
        except Exception as e:
            logger.error(f"Error getting customer: {e}")
            return None
    
    def create_case(self, account_id: str, subject: str, description: str):
        """Create support case in Salesforce."""
        try:
            case = self.sf.Case.create({
                "AccountId": account_id,
                "Subject": subject,
                "Description": description,
                "Status": "New",
                "Priority": "Medium"
            })
            return case
        except Exception as e:
            logger.error(f"Error creating case: {e}")
            return None
    
    def update_case(self, case_id: str, data: dict):
        """Update case in Salesforce."""
        try:
            self.sf.Case.update(case_id, data)
            return True
        except Exception as e:
            logger.error(f"Error updating case: {e}")
            return False
    
    def process_customer_inquiry(self, customer_id: str, inquiry: str):
        """Process customer inquiry using agent."""
        # Get customer data
        customer = self.get_customer_data(customer_id)
        
        # Add context to inquiry
        context = f"Customer: {customer['Name']}\n{inquiry}"
        
        # Process with agent
        response, _ = self.agent.process_input(context)
        
        # Create/update case
        case = self.create_case(
            account_id=customer_id,
            subject=inquiry[:80],
            description=response
        )
        
        return case

# Usage
sf_integration = SalesforceIntegration(
    username="your_email@example.com",
    password="your_password",
    security_token="your_token"
)