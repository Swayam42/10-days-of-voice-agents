import json
import os
from datetime import datetime
from typing import Dict, Optional

class OrderManager:
    def __init__(self, orders_dir: str = "orders"):
        self.orders_dir = orders_dir
        # Create orders directory if it doesn't exist
        os.makedirs(orders_dir, exist_ok=True)
        self.order_counter_file = os.path.join(orders_dir, "_counter.json")
        self._init_counter()
    
    def _init_counter(self):
        """Initialize or load the order counter"""
        if os.path.exists(self.order_counter_file):
            with open(self.order_counter_file, 'r') as f:
                data = json.load(f)
                self.counter = data.get('last_order_id', 0)
        else:
            self.counter = 0
            self._save_counter()
    
    def _save_counter(self):
        """Save the current counter value"""
        with open(self.order_counter_file, 'w') as f:
            json.dump({'last_order_id': self.counter}, f)
    
    def _generate_order_id(self) -> str:
        """Generate a new order ID"""
        self.counter += 1
        self._save_counter()
        return f"GW{self.counter:06d}"
    
    def create_order(self, cart_data: Dict, customer_info: Optional[Dict] = None, payment_method: str = "COD") -> Dict:
        """Create and save a new order"""
        order_id = self._generate_order_id()
        timestamp = datetime.now().isoformat()
        
        order = {
            "order_id": order_id,
            "timestamp": timestamp,
            "date": datetime.now().strftime("%d %B %Y"),
            "time": datetime.now().strftime("%I:%M %p"),
            "status": "placed",
            "items": cart_data['items'],
            "total_amount": cart_data['total'],
            "item_count": cart_data['item_count'],
            "customer_info": customer_info or {
                "name": "Guest Customer",
                "phone": None,
                "address": None
            },
            "payment_method": payment_method.upper(),
            "upi_id": "swayam.jethi@okhdfcbank" if payment_method.upper() == "UPI" else None,
            "delivery_instructions": None
        }
        
        # Save order to file
        order_filename = os.path.join(self.orders_dir, f"order_{order_id}.json")
        with open(order_filename, 'w', encoding='utf-8') as f:
            json.dump(order, f, indent=2, ensure_ascii=False)
        
        return order
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """Retrieve an order by ID"""
        order_filename = os.path.join(self.orders_dir, f"order_{order_id}.json")
        
        if not os.path.exists(order_filename):
            return None
        
        with open(order_filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_order_status(self, order_id: str, new_status: str) -> bool:
        """Update order status"""
        order = self.get_order(order_id)
        
        if not order:
            return False
        
        order['status'] = new_status
        order['status_updated_at'] = datetime.now().isoformat()
        
        order_filename = os.path.join(self.orders_dir, f"order_{order_id}.json")
        with open(order_filename, 'w', encoding='utf-8') as f:
            json.dump(order, f, indent=2, ensure_ascii=False)
        
        return True
    
    def get_order_summary(self, order: Dict) -> str:
        """Get a formatted summary of an order"""
        summary_lines = [
            f"Order #{order['order_id']}",
            f"Date: {order['date']} at {order['time']}",
            f"Status: {order['status'].upper()}",
            f"\nItems:"
        ]
        
        for item in order['items']:
            summary_lines.append(
                f"- {item['quantity']}x {item['name']} - ₹{item['price'] * item['quantity']}"
            )
        
        summary_lines.append(f"\nTotal: ₹{order['total_amount']}")
        summary_lines.append(f"Payment: {order['payment_method']}")
        
        return "\n".join(summary_lines)
    
    def list_recent_orders(self, limit: int = 5) -> list:
        """Get list of recent orders"""
        order_files = [f for f in os.listdir(self.orders_dir) if f.startswith('order_')]
        order_files.sort(reverse=True)  # Most recent first
        
        orders = []
        for order_file in order_files[:limit]:
            order_path = os.path.join(self.orders_dir, order_file)
            with open(order_path, 'r', encoding='utf-8') as f:
                orders.append(json.load(f))
        
        return orders