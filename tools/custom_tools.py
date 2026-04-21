from __future__ import annotations

import logging
import json
from typing import Dict, List
from datetime import datetime, timedelta
from langchain.tools import BaseTool

logger = logging.getLogger(__name__)


class OrderLookupTool(BaseTool):
    name = "order_lookup"
    description = (
        "Look up order information by order ID or customer email. "
        "Returns order status, items, and tracking information. "
        "Input: Order ID (e.g., 'ORD123456') or customer email"
    )
    
    def __init__(self):
        super().__init__()
        self.orders_db = self._generate_sample_orders()
    
    def _generate_sample_orders(self) -> Dict:
        return {
            "ORD001": {
                "customer": "customer@example.com",
                "order_date": "2024-01-15",
                "items": [
                    {"product": "Premium Wireless Headphones", "quantity": 1, "price": 199.99}
                ],
                "status": "Delivered",
                "tracking": "TRACK123456",
                "delivery_date": "2024-01-20"
            },
            "ORD002": {
                "customer": "john@example.com",
                "order_date": "2024-01-18",
                "items": [
                    {"product": "Smart Watch Pro", "quantity": 1, "price": 299.99}
                ],
                "status": "In Transit",
                "tracking": "TRACK789012",
                "expected_delivery": "2024-01-25"
            }
        }
    
    def _run(self, order_id: str) -> str:
        try:
            if order_id.upper() in self.orders_db:
                order = self.orders_db[order_id.upper()]
                return self._format_order(order_id.upper(), order)
            
            for oid, order in self.orders_db.items():
                if order.get("customer").lower() == order_id.lower():
                    return self._format_order(oid, order)
            
            return f"Order not found for: {order_id}"
        
        except Exception as e:
            logger.error(f"Error looking up order: {e}")
            return f"Error looking up order: {str(e)}"
    
    def _format_order(self, order_id: str, order: Dict) -> str:
        items_str = "\n".join([
            f"  - {item['product']} (Qty: {item['quantity']}, Price: ${item['price']})"
            for item in order.get("items", [])
        ])
        
        total = sum(item["price"] * item["quantity"] for item in order.get("items", []))
        
        result = f"""
Order ID: {order_id}
Customer: {order['customer']}
Order Date: {order['order_date']}
Status: {order['status']}

Items:
{items_str}

Total: ${total:.2f}
Tracking Number: {order.get('tracking', 'N/A')}

Expected Delivery: {order.get('expected_delivery', order.get('delivery_date', 'N/A'))}
"""
        return result
    
    async def _arun(self, order_id: str) -> str:
        return self._run(order_id)


class CreateSupportTicketTool(BaseTool):
    name = "create_support_ticket"
    description = (
        "Create a support ticket for issues that cannot be resolved by the agent. "
        "Input: Comma-separated values (customer_email, subject, description)"
    )
    
    def __init__(self):
        super().__init__()
        self.tickets = {}
        self.next_id = 1001
    
    def _run(self, input_str: str) -> str:
        try:
            parts = input_str.split("|")
            if len(parts) < 3:
                return "Error: Please provide email|subject|description"
            
            email = parts[0].strip()
            subject = parts[1].strip()
            description = parts[2].strip()
            
            ticket_id = f"TICKET{self.next_id}"
            self.next_id += 1
            
            ticket = {
                "id": ticket_id,
                "customer_email": email,
                "subject": subject,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "status": "Open",
                "priority": "Medium"
            }
            
            self.tickets[ticket_id] = ticket
            
            return f"""
Support Ticket Created Successfully!
Ticket ID: {ticket_id}
Subject: {subject}
Status: Open

A support representative will contact you at {email} within 24 hours.
Please reference your ticket ID in any follow-up communications.
"""
        
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            return f"Error creating support ticket: {str(e)}"
    
    async def _arun(self, input_str: str) -> str:
        return self._run(input_str)


class PricingInfoTool(BaseTool):
    name = "pricing_info"
    description = (
        "Get pricing information and current promotions. "
        "Input: Product name or 'all' for all promotions"
    )
    
    def __init__(self):
        super().__init__()
    
    def _run(self, query: str) -> str:
        try:
            promotions = {
                "headphones": "Premium Wireless Headphones - $199.99 (Normally $249.99) - 20% OFF",
                "smartwatch": "Smart Watch Pro - $299.99 (Free shipping on orders over $50)",
                "charger": "USB-C Fast Charger - $49.99 (Buy 2, Get 15% off)",
                "ssd": "Portable SSD 1TB - $149.99 (Extended 3-year warranty included)",
                "keyboard": "Mechanical Keyboard - $159.99 (RGB lighting included)"
            }
            
            if query.lower() == "all":
                result = "Current Promotions:\n"
                for promo in promotions.values():
                    result += f"• {promo}\n"
                return result
            
            for key, promo in promotions.items():
                if key in query.lower():
                    return f"Promotion: {promo}"
            
            return f"No specific promotion found for '{query}'. Check our website for all current offers."
        
        except Exception as e:
            logger.error(f"Error getting pricing: {e}")
            return f"Error retrieving pricing information: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class CalculateShippingTool(BaseTool):
    name = "calculate_shipping"
    description = (
        "Calculate shipping cost and delivery time. "
        "Input: shipping_method|zip_code (e.g., 'standard|12345' or 'express|67890')"
    )
    
    def __init__(self):
        super().__init__()
    
    def _run(self, input_str: str) -> str:
        try:
            parts = input_str.split("|")
            if len(parts) < 2:
                return "Error: Please provide method|zipcode"
            
            method = parts[0].strip().lower()
            zip_code = parts[1].strip()
            
            shipping_rates = {
                "standard": {"cost": 0, "days": 7, "name": "Standard Shipping (Free)"},
                "express": {"cost": 10, "days": 3, "name": "Express Shipping"},
                "overnight": {"cost": 25, "days": 1, "name": "Overnight Shipping"}
            }
            
            if method not in shipping_rates:
                return f"Invalid shipping method. Choose from: {', '.join(shipping_rates.keys())}"
            
            rate = shipping_rates[method]
            delivery_date = datetime.now() + timedelta(days=rate["days"])
            
            return f"""
Shipping Calculation:
Method: {rate['name']}
Cost: ${rate['cost']}
Estimated Delivery: {delivery_date.strftime('%B %d, %Y')} ({rate['days']} business days)
"""
        
        except Exception as e:
            logger.error(f"Error calculating shipping: {e}")
            return f"Error calculating shipping: {str(e)}"
    
    async def _arun(self, input_str: str) -> str:
        return self._run(input_str)


def get_custom_tools() -> List[BaseTool]:
    return [
        OrderLookupTool(),
        CreateSupportTicketTool(),
        PricingInfoTool(),
        CalculateShippingTool()
    ]