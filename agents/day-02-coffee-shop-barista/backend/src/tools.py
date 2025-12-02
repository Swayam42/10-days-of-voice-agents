"""
Function Tools for Coffee Barista Agent
"""

import logging
from typing import Annotated, Literal
from livekit.agents import function_tool, RunContext, ToolError
from pydantic import Field
from order_state import (
    OrderState, 
    MENU, 
    KRUTI_LOCATIONS,
    normalize_drink_name,
    normalize_size,
    normalize_milk,
    normalize_location,
    is_valid_drink,
    is_valid_size,
    is_valid_milk,
    is_valid_location,
)

logger = logging.getLogger("coffee-tools")


class Userdata:
    """Container for conversation state"""
    def __init__(self):
        self.order = OrderState()


@function_tool
async def set_drink_type(
    ctx: RunContext[Userdata],
    drink: Annotated[
        Literal[
            "cappuccino",
            "latte", 
            "espresso",
            "cold_coffee",
            "filter_coffee",
            "americano"
        ],
        Field(description="The type of coffee drink the customer wants. Use 'cold_coffee' for cold coffee, 'filter_coffee' for filter coffee.")
    ]
) -> str:
    """
    Set the drink type for the current order.
    
    Call this IMMEDIATELY when the customer specifies what coffee they want.
    Examples: 
    - User says "cappuccino" or "I want a cappuccino" → call with drink="cappuccino"
    - User says "cold coffee" → call with drink="cold_coffee" 
    - User says "filter coffee" → call with drink="filter_coffee"
    """
    try:
        logger.info(f"🔥 set_drink_type called with: {drink}")
        ctx.userdata.order.drinkType = drink
        logger.info(f"✓ Successfully stored drink: {ctx.userdata.order.drinkType}")
        return f"Perfect! One {drink.replace('_', ' ')}. What size would you like - small, medium, or large?"
    except Exception as e:
        logger.error(f"❌ ERROR setting drink: {e}", exc_info=True)
        ctx.userdata.order.drinkType = drink
        return f"Got it! One {drink.replace('_', ' ')}. What size?"


@function_tool
async def set_size(
    ctx: RunContext[Userdata],
    size: Annotated[
        Literal["small", "medium", "large"],
        Field(description="The size of the drink: small, medium, or large")
    ]
) -> str:
    """
    Set the size for the current order.
    
    Call this when the customer specifies the size.
    Examples: "Medium please", "I'll take a large", "Small is fine"
    """
    try:
        logger.info(f"🔥 set_size called with: {size}")
        ctx.userdata.order.size = size.lower()
        logger.info(f"✓ Successfully stored size: {ctx.userdata.order.size}")
        return f"Awesome, {size} size! What kind of milk would you like? We have full cream, oat, almond, soy, or skimmed."
    except Exception as e:
        logger.error(f"❌ ERROR setting size: {e}", exc_info=True)
        ctx.userdata.order.size = size.lower()
        return f"Perfect, {size}! What milk?"


@function_tool
async def set_milk_type(
    ctx: RunContext[Userdata],
    milk: Annotated[
        Literal["full_cream", "skimmed", "oat", "almond", "soy"],
        Field(description="Type of milk for the drink")
    ]
) -> str:
    """
    Set the milk type for the current order.
    
    Call this when the customer specifies milk preference.
    Examples: "Oat milk please", "Regular milk", "Can I get almond milk?"
    """
    try:
        logger.info(f"🔥 set_milk_type called with: {milk}")
        ctx.userdata.order.milk = milk.lower()
        logger.info(f"✓ Successfully stored milk: {ctx.userdata.order.milk}")
        return f"Great choice! {milk.replace('_', ' ')} milk. Would you like any extras like vanilla, caramel, extra shot, chocolate, hazelnut, or whipped cream? Or no extras is fine too!"
    except Exception as e:
        logger.error(f"❌ ERROR setting milk: {e}", exc_info=True)
        ctx.userdata.order.milk = milk.lower()
        return f"Perfect! Any extras?"


@function_tool
async def add_extra(
    ctx: RunContext[Userdata],
    extra: Annotated[
        Literal["extra_shot", "caramel", "vanilla", "chocolate", "hazelnut", "whipped_cream"],
        Field(description="Extra item to add to the drink")
    ]
) -> str:
    """
    Add an extra item to the current order.
    
    Call this when customer wants to add something extra.
    Can be called multiple times for multiple extras.
    Examples: "Add an extra shot", "With vanilla please", "Can I get caramel?"
    """
    try:
        extra_key = extra.lower()
        
        if extra_key not in ctx.userdata.order.extras:
            ctx.userdata.order.extras.append(extra_key)
            price = MENU["extras"].get(extra_key, 30)
            logger.info(f"✓ Successfully added extra: {extra_key}")
            return f"Added {extra.replace('_', ' ')} for ₹{price}! Anything else or shall we move on?"
        else:
            return f"You already have {extra.replace('_', ' ')}! Anything else?"
    except Exception as e:
        logger.error(f"Error adding extra: {e}")
        ctx.userdata.order.extras.append(extra.lower())
        return f"Added {extra.replace('_', ' ')}! What else?"
    else:
        return f"You already have {extra.replace('_', ' ')} in your order!"


@function_tool
async def set_customer_name(
    ctx: RunContext[Userdata],
    name: Annotated[str, Field(description="Customer's name for the order")]
) -> str:
    """
    Set the customer's name for the order.
    
    Call this when the customer provides their name.
    Examples: "My name is Priya", "Under the name Raj", "It's Amit"
    """
    ctx.userdata.order.name = name.strip().title()
    logger.info(f"Set customer name: {name}")
    return f"Perfect, {name}! "


@function_tool
async def set_location(
    ctx: RunContext[Userdata],
    location: Annotated[
        Literal[
            "bhubaneswar_patia",
            "bhubaneswar_rajmahal_square",
            "bhubaneswar_pal_heights",
            "mumbai_goregaon",
            "cuttack_cda_sector_09",
            "koraput",
            "berhampur",
            "chattisgarh_raipur",
            "bistupur_jamshedpur"
        ],
        Field(description="Kruti Coffee location for pickup")
    ]
) -> str:
    """
    Set the pickup location for the order.
    
    Call this when customer mentions which Kruti Coffee location.
    Examples: "The Patia location", "Rajmahal Square please", "Goregaon branch"
    """
    ctx.userdata.order.location = location.lower()
    logger.info(f"Set location: {location}")
    return f"Great! Pickup at Kruti Coffee {location.replace('_', ' ').title()}."


@function_tool
async def get_order_summary(ctx: RunContext[Userdata]) -> str:
    """
    Get the current order summary.
    
    Call this when:
    - Customer asks "What's my order?"
    - You need to confirm details
    - Before finalizing the order
    """
    order = ctx.userdata.order
    
    if not order.drinkType:
        return "Your order is empty. What would you like to order?"
    
    try:
        order.calculate_price()
    except Exception as e:
        logger.error(f"Error calculating price: {e}")
        order.total_price = 0
    
    summary_parts = ["Here's your order so far:"]
    
    try:
        if order.drinkType:
            drink_name = str(order.drinkType).replace('_', ' ').title()
            summary_parts.append(f"- {drink_name}")
        
        if order.size:
            summary_parts.append(f"- Size: {str(order.size).title()}")
        
        if order.milk:
            milk_name = str(order.milk).replace('_', ' ').title()
            summary_parts.append(f"- Milk: {milk_name}")
        
        if order.extras:
            extras_str = ", ".join([str(e).replace("_", " ").title() for e in order.extras])
            summary_parts.append(f"- Extras: {extras_str}")
        
        if order.name:
            summary_parts.append(f"- Name: {str(order.name)}")
        
        if order.location:
            loc_name = str(order.location).replace('_', ' ').title()
            summary_parts.append(f"- Location: {loc_name}")
        
        summary_parts.append(f"- Total: ₹{order.total_price}")
        
        return "\n".join(summary_parts)
    except Exception as e:
        logger.error(f"Error generating summary: {e}", exc_info=True)
        return f"Order for {order.name}: {order.drinkType}, {order.size}, {order.milk} milk. Total: ₹{order.total_price}"


@function_tool
async def finalize_order(ctx: RunContext[Userdata]) -> str:
    """
    Finalize and save the completed order.
    
    Call this ONLY when:
    - All required fields are filled
    - Customer confirms they're ready to place the order
    
    This will save the order to a JSON file.
    """
    order = ctx.userdata.order
    
    # Check if order has minimum required fields
    logger.info(f"🔥 finalize_order called - drinkType: {order.drinkType}, size: {order.size}, milk: {order.milk}, name: {order.name}")
    
    if not order.is_complete():
        missing = []
        if not order.drinkType: missing.append("drink type")
        if not order.size: missing.append("size")
        if not order.milk: missing.append("milk type")
        if not order.name: missing.append("customer name")
        
        logger.warning(f"Order incomplete. Missing: {', '.join(missing)}")
        return f"I still need a few details: {', '.join(missing)}. Can you provide those?"
    
    # Calculate price
    order.calculate_price()
    logger.info(f"✓ Price calculated: ₹{order.total_price}")
    
    # Save order
    try:
        logger.info(f"🔥 Attempting to save order for {order.name}")
        filepath = order.save_to_file()
        logger.info(f"✓ Order saved successfully: {filepath}")
    except Exception as e:
        logger.error(f"❌ Error saving order file: {e}", exc_info=True)
        # Continue anyway - file save is not critical
    
    # Generate summary
    try:
        summary = order.get_summary()
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        summary = f"Order for {order.name}: {order.drinkType} ({order.size}), {order.milk} milk"
    
    location_text = order.location.replace('_', ' ').title() if order.location else 'your selected location'
    
    return f"""Perfect! Your order is confirmed! 

{summary}

Order ID: {order.order_id}

Your order will be ready in 5-7 minutes at Kruti Coffee {location_text}.

Thank you for choosing Kruti Coffee! Have a great day!"""


@function_tool
async def cancel_order(ctx: RunContext[Userdata]) -> str:
    """
    Cancel the current order and start fresh.
    
    Call this when customer wants to cancel or start over.
    Examples: "Cancel this order", "Let me start again", "Never mind"
    """
    ctx.userdata.order = OrderState()
    logger.info("Order cancelled")
    return "No problem! Order cancelled. Would you like to start a new order?"


# Export all tools
ALL_TOOLS = [
    set_drink_type,
    set_size,
    set_milk_type,
    add_extra,
    set_customer_name,
    set_location,
    get_order_summary,
    finalize_order,
    cancel_order,
]
