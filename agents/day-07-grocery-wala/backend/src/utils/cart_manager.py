import json
import os
from typing import Dict, List, Optional

class CartManager:
    def __init__(self, catalog_path: str = "catalog.json"):
        with open(catalog_path, 'r', encoding='utf-8') as f:
            self.catalog = json.load(f)
        self.cart: Dict[str, Dict] = {}
        self._build_item_index()
        
        # Ensure current_cart.json exists
        self._ensure_cart_file_exists()
    
    def _build_item_index(self):
        """Build a quick lookup index for items by ID and name"""
        self.item_index = {}
        for category_key, category_data in self.catalog['categories'].items():
            for item in category_data['items']:
                self.item_index[item['id']] = {
                    **item,
                    'category': category_key
                }
                # Also index by lowercase name for flexible matching
                self.item_index[item['name'].lower()] = {
                    **item,
                    'category': category_key
                }
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for fuzzy matching - remove common variations"""
        normalized = text.lower().strip()
        # Remove common filler words and variations
        normalized = normalized.replace('on', 'corn').replace('con', 'corn')
        # Normalize double letters
        normalized = normalized.replace('chhese', 'cheese').replace('chees', 'cheese')
        normalized = normalized.replace('panner', 'paneer').replace('panir', 'paneer').replace('paner', 'paneer')
        normalized = normalized.replace('daal', 'dal').replace('chwal', 'chawal').replace('chawl', 'chawal')
        normalized = normalized.replace('basmatti', 'basmati').replace('basmti', 'basmati').replace('rise', 'rice')
        normalized = normalized.replace('aata', 'atta').replace('ata', 'atta')
        return normalized
    
    def find_item(self, query: str) -> Optional[Dict]:
        """Find item by ID or name with fuzzy matching for pronunciation variations"""
        # Try exact ID match first
        if query in self.item_index:
            return self.item_index[query]
        
        # Try lowercase name match
        if query.lower() in self.item_index:
            return self.item_index[query.lower()]
        
        # Try normalized fuzzy matching
        query_normalized = self._normalize_text(query)
        for key, item in self.item_index.items():
            if isinstance(key, str):
                key_normalized = self._normalize_text(key)
                if query_normalized == key_normalized or query_normalized in key_normalized:
                    return item
        
        # Try partial matching on original query
        query_lower = query.lower()
        for key, item in self.item_index.items():
            if isinstance(key, str) and query_lower in key.lower():
                return item
        
        return None
    
    def add_item(self, item_identifier: str, quantity: int = 1) -> Dict:
        """Add item to cart. Returns dict with success status and message"""
        item = self.find_item(item_identifier)
        
        if not item:
            return {
                "success": False,
                "message": f"Sorry, I couldn't find '{item_identifier}' in our catalog"
            }
        
        item_id = item['id']
        
        if item_id in self.cart:
            self.cart[item_id]['quantity'] += quantity
            action = "updated"
        else:
            self.cart[item_id] = {
                **item,
                'quantity': quantity
            }
            action = "added"
        
        # Export cart to JSON for UI
        self.export_to_json()
        
        return {
            "success": True,
            "action": action,
            "item": item,
            "quantity": self.cart[item_id]['quantity'],
            "message": f"{action.capitalize()} {quantity} {item['name']} to cart"
        }
    
    def remove_item(self, item_identifier: str) -> Dict:
        """Remove item from cart completely"""
        item = self.find_item(item_identifier)
        
        if not item:
            return {
                "success": False,
                "message": f"Item '{item_identifier}' not found"
            }
        
        item_id = item['id']
        
        if item_id not in self.cart:
            return {
                "success": False,
                "message": f"{item['name']} is not in your cart"
            }
        
        removed_item = self.cart.pop(item_id)
        
        # Export cart to JSON for UI
        self.export_to_json()
        
        return {
            "success": True,
            "message": f"Removed {removed_item['name']} from cart"
        }
    
    def update_quantity(self, item_identifier: str, quantity: int) -> Dict:
        """Update quantity of an item in cart"""
        if quantity <= 0:
            return self.remove_item(item_identifier)
        
        item = self.find_item(item_identifier)
        
        if not item:
            return {
                "success": False,
                "message": f"Item '{item_identifier}' not found"
            }
        
        item_id = item['id']
        
        if item_id not in self.cart:
            return self.add_item(item_identifier, quantity)
        
        self.cart[item_id]['quantity'] = quantity
        
        # Export cart to JSON for UI
        self.export_to_json()
        
        return {
            "success": True,
            "message": f"Updated {item['name']} quantity to {quantity}"
        }
    
    def get_cart_summary(self) -> str:
        """Get a formatted string of cart contents"""
        if not self.cart:
            return "Your cart is empty"
        
        summary_lines = ["Your cart:"]
        total = 0
        
        for item_id, cart_item in self.cart.items():
            item_total = cart_item['price'] * cart_item['quantity']
            total += item_total
            summary_lines.append(
                f"- {cart_item['quantity']}x {cart_item['name']} ({cart_item['unit']}) - ₹{item_total}"
            )
        
        summary_lines.append(f"\nTotal: ₹{total}")
        return "\n".join(summary_lines)
    
    def get_cart_data(self) -> Dict:
        """Get cart data as a dictionary"""
        return {
            "items": list(self.cart.values()),
            "total": self.calculate_total(),
            "item_count": sum(item['quantity'] for item in self.cart.values())
        }
    
    def calculate_total(self) -> float:
        """Calculate total cart value"""
        return sum(item['price'] * item['quantity'] for item in self.cart.values())
    
    def clear_cart(self):
        """Empty the cart"""
        self.cart = {}
        
        # Export empty cart to JSON for UI
        self.export_to_json()
    
    def is_empty(self) -> bool:
        """Check if cart is empty"""
        return len(self.cart) == 0
    
    def get_item_count(self) -> int:
        """Get total number of items in cart"""
        return sum(item['quantity'] for item in self.cart.values())
    
    def _ensure_cart_file_exists(self):
        """Ensure current_cart.json exists with empty cart data"""
        orders_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'orders')
        os.makedirs(orders_dir, exist_ok=True)
        filepath = os.path.join(orders_dir, 'current_cart.json')
        
        if not os.path.exists(filepath):
            # Create empty cart file
            empty_cart = {
                "items": [],
                "total": 0,
                "item_count": 0
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(empty_cart, f, indent=2, ensure_ascii=False)
    
    def export_to_json(self, filepath: str = None):
        """Export current cart to JSON file for UI to read"""
        if filepath is None:
            # Default to orders directory
            orders_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'orders')
            os.makedirs(orders_dir, exist_ok=True)
            filepath = os.path.join(orders_dir, 'current_cart.json')
        
        cart_data = self.get_cart_data()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cart_data, f, indent=2, ensure_ascii=False)