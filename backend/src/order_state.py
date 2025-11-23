"""
Order State Management for Kruti Coffee Barista
"""

import json
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional


# Kruti Coffee Menu
MENU = {
    "drinks": {
        "cappuccino": {"small": 120, "medium": 150, "large": 180},
        "latte": {"small": 130, "medium": 160, "large": 190},
        "espresso": {"small": 100, "medium": 130, "large": 160},
        "cold_coffee": {"small": 140, "medium": 170, "large": 200},
        "filter_coffee": {"small": 80, "medium": 100, "large": 130},
        "americano": {"small": 110, "medium": 140, "large": 170},
    },
    "milk_options": ["full_cream", "skimmed", "oat", "almond", "soy"],
    "extras": {
        "extra_shot": 40,
        "caramel": 30,
        "vanilla": 30,
        "chocolate": 30,
        "hazelnut": 30,
        "whipped_cream": 20,
    }
}

KRUTI_LOCATIONS = [
    "bhubaneswar_patia",
    "bhubaneswar_rajmahal_square",
    "bhubaneswar_pal_heights",
    "mumbai_goregaon",
    "cuttack_cda_sector_09",
    "koraput",
    "berhampur",
    "chattisgarh_raipur",
    "bistupur_jamshedpur"
]


@dataclass
class OrderState:
    """Represents a single coffee order"""
    order_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: Optional[str] = None
    
    # Order details (matching the required format)
    drinkType: Optional[str] = None
    size: Optional[str] = None
    milk: Optional[str] = None
    extras: list[str] = field(default_factory=list)
    name: Optional[str] = None
    
    # Additional fields
    location: Optional[str] = None
    base_price: int = 0
    extras_price: int = 0
    total_price: int = 0
    
    def is_complete(self) -> bool:
        """Check if all required fields are filled"""
        return all([
            self.drinkType,
            self.size,
            self.milk,
            self.name,
        ])
    
    def calculate_price(self) -> int:
        """Calculate the total price of the order"""
        if self.drinkType and self.size:
            self.base_price = MENU["drinks"].get(self.drinkType, {}).get(self.size, 0)
        
        self.extras_price = sum(
            MENU["extras"].get(extra, 0) 
            for extra in self.extras
        )
        
        self.total_price = self.base_price + self.extras_price
        return self.total_price
    
    def to_dict(self) -> dict:
        """Convert order to dictionary for saving"""
        return {
            "order_id": self.order_id,
            "timestamp": self.timestamp or datetime.now().isoformat(),
            "drinkType": self.drinkType,
            "size": self.size,
            "milk": self.milk,
            "extras": self.extras,
            "name": self.name,
            "location": self.location,
            "base_price": self.base_price,
            "extras_price": self.extras_price,
            "total_price": self.total_price,
        }
    
    def get_summary(self) -> str:
        """Generate a human-readable summary"""
        try:
            extras_str = ", ".join([str(e).replace("_", " ").title() for e in self.extras]) if self.extras else "None"
            location_str = str(self.location).replace("_", " ").title() if self.location else "Not specified"
            drink_str = str(self.drinkType).replace("_", " ").title() if self.drinkType else "Unknown"
            size_str = str(self.size).title() if self.size else "Unknown"
            milk_str = str(self.milk).replace("_", " ").title() if self.milk else "Unknown"
            name_str = str(self.name) if self.name else "Unknown"
            
            return f"""Order Summary for {name_str}:
- Drink: {drink_str}
- Size: {size_str}
- Milk: {milk_str}
- Extras: {extras_str}
- Location: {location_str}
- Total Price: ₹{self.total_price}"""
        except Exception as e:
            return f"Order for {self.name}: Total ₹{self.total_price}"
    
    def save_to_file(self, directory: str = "orders") -> str:
        """Save the order to a JSON file"""
        import os
        
        # Create orders directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Update timestamp and price
        self.timestamp = datetime.now().isoformat()
        self.calculate_price()
        
        # Create safe filename
        safe_name = self.name.replace(' ', '_') if self.name else "unknown"
        filename = f"{directory}/order_{self.order_id}_{safe_name}.json"
        
        # Save to file
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            print(f"✓ Order saved successfully: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error saving order: {e}")
            raise


# Helper functions
def normalize_drink_name(drink: str) -> str:
    """Convert user input to menu key"""
    return drink.lower().replace(" ", "_").replace("-", "_")


def normalize_size(size: str) -> str:
    """Convert user input to standard size"""
    size_map = {
        "s": "small", "small": "small",
        "m": "medium", "medium": "medium", "regular": "medium",
        "l": "large", "large": "large", "grande": "large"
    }
    return size_map.get(size.lower(), size.lower())


def normalize_milk(milk: str) -> str:
    """Convert user input to menu key"""
    return milk.lower().replace(" milk", "").replace(" ", "_")


def normalize_location(location: str) -> str:
    """Convert user input to location key"""
    return location.lower().replace(" ", "_").replace("-", "_")


def is_valid_drink(drink: str) -> bool:
    """Check if drink exists in menu"""
    return normalize_drink_name(drink) in MENU["drinks"]


def is_valid_size(size: str) -> bool:
    """Check if size is valid"""
    return normalize_size(size) in ["small", "medium", "large"]


def is_valid_milk(milk: str) -> bool:
    """Check if milk option exists"""
    return normalize_milk(milk) in MENU["milk_options"]


def is_valid_extra(extra: str) -> bool:
    """Check if extra exists in menu"""
    extra_key = extra.lower().replace(" ", "_")
    return extra_key in MENU["extras"]


def is_valid_location(location: str) -> bool:
    """Check if location is valid"""
    return normalize_location(location) in KRUTI_LOCATIONS
