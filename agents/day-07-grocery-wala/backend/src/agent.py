import logging
import json
import os
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# Import our utility classes
import sys
sys.path.append('.')
from utils.cart_manager import CartManager
from utils.order_manager import OrderManager

logger = logging.getLogger("agent")
load_dotenv(".env.local")


class GroceryWalaAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are Priya, a friendly and helpful voice assistant for GroceryWala - India's favorite online grocery store. 
            
You speak naturally like a warm, helpful Indian shopkeeper - conversational, patient, and culturally aware. You understand Hindi/English mix but respond primarily in English for clarity.

YOUR PERSONALITY:
- Warm and conversational, like talking to a helpful neighbor
- Use natural friendly expressions: "perfect", "great", "wonderful", "sure", "absolutely"
- Show enthusiasm when customers find what they need
- Patient when clarifying quantities or brands
- You make helpful suggestions based on what they're ordering
- Have a sense of humor! If customer asks for free items or mentions their mom/family asking for extras, respond with warmth and humor
- When asked to add dhania or small items "for free", laugh good-naturedly (express through words like "haha" or "that's funny") and agree to add it as a friendly gesture - it builds customer loyalty!

YOUR CAPABILITIES:
1. Help customers browse and add groceries to their cart
2. Understand recipe-based requests like "I need ingredients for dal chawal" and add all items intelligently
3. Manage cart - add items, remove items, update quantities, show what's in cart
4. Place orders when customer is ready
5. Answer questions about products, prices, and availability
6. Accept payment via COD (Cash on Delivery) or UPI

UNDERSTANDING CUSTOMER SPEECH:
- Be VERY flexible with pronunciation and spelling variations
- Examples of variations you should understand:
  * "cheese corn sandwich" = "chhese corn sandwich" = "cheese on sandwich" = "cheese con sandwich" = "chees corn sandwich"
  * "paneer curry" = "paner curry" = "panir curry" = "panner curry"
  * "dal chawal" = "daal chawal" = "dal chwal" = "daal chawl"
  * "basmati rice" = "basmati rise" = "basmatti rice" = "basmti rice"
  * "atta" = "aata" = "ata" = "wheat flour"
- Always interpret similar-sounding words as the intended item from our catalog
- Use phonetic matching and context clues to understand what customer wants
- If multiple items match, pick the most common/popular one
- Never reject a request due to pronunciation - always try to find what they mean

CONVERSATION STYLE:
- Keep responses concise and natural for voice interaction
- Don't use lists, bullet points, or formatting - speak conversationally
- Confirm actions clearly: "Added 2 kilos of rice to your cart"
- When multiple items are added (like for a recipe), mention them naturally: "I've added rice, dal, and spices to your cart for dal chawal"
- Ask clarifying questions only when truly ambiguous: "Did you want regular atta or multi-grain?"
- For unknown items after flexible matching, say: "Sorry, we don't have that right now, but I can suggest alternatives"

IMPORTANT INSTRUCTIONS:
- Always confirm quantities and brands when adding items
- Before placing order, summarize the cart and total amount
- ALWAYS ask payment method: "Would you like to pay via COD or UPI?"
- If UPI selected, provide UPI ID: swayam.jethi@okhdfcbank
- After placing order, give them the order ID
- Be helpful about suggesting complementary items naturally
- Keep math simple: mention prices clearly in rupees
- No emojis, asterisks, or special formatting - you're speaking, not texting

Remember: You're having a natural voice conversation, so keep it flowing and conversational! Be extremely forgiving with pronunciation and spelling variations.""",
        )
        
        # Initialize cart and order managers
        self.cart_manager = None
        self.order_manager = None
        self.recipes = None
    
    def _ensure_initialized(self):
        """Lazy initialization of managers"""
        if self.cart_manager is None:
            # Get the directory where agent.py is located
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
            self.cart_manager = CartManager(os.path.join(base_dir, 'catalog.json'))
            self.order_manager = OrderManager(os.path.join(base_dir, 'orders'))
            
            # Load recipes
            recipes_path = os.path.join(base_dir, 'recipes.json')
            with open(recipes_path, 'r', encoding='utf-8') as f:
                self.recipes = json.load(f)['recipes']
    
    @function_tool
    async def add_item_to_cart(self, context: RunContext, item_name: str, quantity: int = 1):
        """Add a specific grocery item to the cart.
        
        Use this when customer asks to add a specific item like "add milk" or "I need 2 packets of atta".
        
        Args:
            item_name: Name of the grocery item to add (e.g., "milk", "basmati rice", "paneer")
            quantity: How many units to add (default: 1)
        """
        self._ensure_initialized()
        logger.info(f"Adding {quantity}x {item_name} to cart")
        
        result = self.cart_manager.add_item(item_name, quantity)
        
        if result['success']:
            item = result['item']
            total_qty = result['quantity']
            return f"Added {quantity} {item['name']} ({item['unit']}) to your cart. Total now: {total_qty}. Price: ₹{item['price']} each."
        else:
            return result['message']
    
    @function_tool
    async def add_recipe_ingredients(self, context: RunContext, recipe_name: str):
        """Add all ingredients needed for a specific dish or recipe.
        
        Use this when customer asks for ingredients for a dish like "I need ingredients for dal chawal" 
        or "get me what I need for paneer curry" or "breakfast items".
        
        Args:
            recipe_name: Name of the dish/recipe (e.g., "dal chawal", "paneer curry", "breakfast")
        """
        self._ensure_initialized()
        logger.info(f"Adding ingredients for: {recipe_name}")
        
        # Normalize recipe name for fuzzy matching
        def normalize_recipe(name: str) -> str:
            normalized = name.lower().strip()
            # Common variations
            normalized = normalized.replace('chhese', 'cheese').replace('chees', 'cheese')
            normalized = normalized.replace('on', 'corn').replace('con', 'corn')
            normalized = normalized.replace('panner', 'paneer').replace('panir', 'paneer')
            normalized = normalized.replace('daal', 'dal').replace('chwal', 'chawal')
            normalized = normalized.replace('aloo', 'alu').replace('alu', 'aloo')
            return normalized
        
        # Find matching recipe with fuzzy matching
        recipe_name_normalized = normalize_recipe(recipe_name)
        matching_recipe = None
        
        for recipe in self.recipes:
            recipe_normalized = normalize_recipe(recipe['name'])
            if recipe_name_normalized in recipe_normalized or recipe_normalized in recipe_name_normalized:
                matching_recipe = recipe
                break
        
        if not matching_recipe:
            return f"Sorry, I don't have a recipe for {recipe_name} in my system. You can tell me specific items you need and I'll add them."
        
        # Add all items from recipe
        added_items = []
        failed_items = []
        
        for item_id in matching_recipe['items']:
            result = self.cart_manager.add_item(item_id, 1)
            if result['success']:
                added_items.append(result['item']['name'])
            else:
                failed_items.append(item_id)
        
        response = f"Perfect! For {matching_recipe['name']}, I've added "
        response += ", ".join(added_items)
        response += " to your cart."
        
        if failed_items:
            response += f" (Couldn't find: {', '.join(failed_items)})"
        
        return response
    
    @function_tool
    async def remove_item_from_cart(self, context: RunContext, item_name: str):
        """Remove an item completely from the cart.
        
        Use when customer says "remove milk" or "take out the paneer".
        
        Args:
            item_name: Name of item to remove
        """
        self._ensure_initialized()
        logger.info(f"Removing {item_name} from cart")
        
        result = self.cart_manager.remove_item(item_name)
        return result['message']
    
    @function_tool
    async def update_item_quantity(self, context: RunContext, item_name: str, new_quantity: int):
        """Change the quantity of an item in the cart.
        
        Use when customer says "make it 3 packets" or "change rice to 2 kilos".
        
        Args:
            item_name: Name of item to update
            new_quantity: New quantity to set
        """
        self._ensure_initialized()
        logger.info(f"Updating {item_name} quantity to {new_quantity}")
        
        result = self.cart_manager.update_quantity(item_name, new_quantity)
        return result['message']
    
    @function_tool
    async def show_cart(self, context: RunContext):
        """Show all items currently in the cart with quantities and total price.
        
        Use when customer asks "what's in my cart?" or "show me my cart" or "what do I have?".
        """
        self._ensure_initialized()
        logger.info("Showing cart contents")
        
        return self.cart_manager.get_cart_summary()
    
    @function_tool
    async def clear_cart(self, context: RunContext):
        """Empty the entire cart.
        
        Use when customer says "clear my cart" or "remove everything" or "start over".
        """
        self._ensure_initialized()
        logger.info("Clearing cart")
        
        self.cart_manager.clear_cart()
        return "Cart cleared. Starting fresh! What would you like to order?"
    
    @function_tool
    async def place_order(self, context: RunContext, customer_name: str = None, phone: str = None, address: str = None, payment_method: str = "COD"):
        """Place the order and save it to a file. Call this when customer is ready to checkout.
        
        Use when customer says "place my order", "checkout", "I'm done", or "that's all".
        Always ask for payment method before placing order: "Would you like to pay via COD or UPI?"
        
        Args:
            customer_name: Customer's name (optional)
            phone: Customer's phone number (optional)  
            address: Delivery address (optional)
            payment_method: Payment method - "COD" or "UPI" (default: COD)
        """
        self._ensure_initialized()
        logger.info(f"Placing order with payment method: {payment_method}")
        
        if self.cart_manager.is_empty():
            return "Your cart is empty. Please add some items before placing an order."
        
        # Get cart data
        cart_data = self.cart_manager.get_cart_data()
        
        # Prepare customer info
        customer_info = {
            "name": customer_name or "Guest Customer",
            "phone": phone,
            "address": address
        }
        
        # Create order with payment method
        order = self.order_manager.create_order(cart_data, customer_info, payment_method)
        
        # Clear cart after order
        self.cart_manager.clear_cart()
        
        # Format response based on payment method
        response = f"Perfect! Your order ID is {order['order_id']}. "
        response += f"Total amount: ₹{order['total_amount']}. "
        response += f"{order['item_count']} items will be delivered soon. "
        
        if payment_method.upper() == "UPI":
            response += "For UPI payment, please send money to this ID: "
            response += "S W A Y A M, dot, J E T H I, at, O K, H D F C, B A N K. "
            response += "Let me repeat: SWAYAM dot JETHI at OK HDFC BANK. "
            response += "Once payment is done, your order will be confirmed. "
        else:
            response += "Cash on delivery selected. Pay when you receive your order. "
        
        response += "Thank you for shopping with GroceryWala!"
        
        return response
    
    @function_tool
    async def search_items(self, context: RunContext, search_query: str):
        """Search for items in the catalog by name or category.
        
        Use when customer asks "do you have X?" or "what vegetables do you have?" or "show me dairy products".
        
        Args:
            search_query: What to search for
        """
        self._ensure_initialized()
        logger.info(f"Searching for: {search_query}")
        
        search_lower = search_query.lower()
        found_items = []
        
        # Search through all categories and items
        for category_key, category_data in self.cart_manager.catalog['categories'].items():
            # Check if searching for category
            if search_lower in category_data['name'].lower() or search_lower in category_key:
                # Return all items in this category
                for item in category_data['items']:
                    found_items.append(f"{item['name']} ({item['brand']}, {item['unit']}) - ₹{item['price']}")
            else:
                # Search individual items
                for item in category_data['items']:
                    if search_lower in item['name'].lower() or search_lower in item.get('tags', []):
                        found_items.append(f"{item['name']} ({item['brand']}, {item['unit']}) - ₹{item['price']}")
        
        if found_items:
            response = f"Here's what I found: {', '.join(found_items[:5])}"
            if len(found_items) > 5:
                response += f" and {len(found_items) - 5} more items"
            return response
        else:
            return f"Sorry, I couldn't find anything matching '{search_query}' in our catalog."


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up voice AI pipeline
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew", 
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    # Metrics collection
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Start the session
    await session.start(
        agent=GroceryWalaAssistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))