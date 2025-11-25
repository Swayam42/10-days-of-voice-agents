import logging
import json
import random
from pathlib import Path
from typing import Annotated
from datetime import datetime

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
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")
load_dotenv(".env.local")


# Global variable to store lead data across function calls
lead_storage = {
    "name": None,
    "company": None,
    "email": None,
    "role": None,
    "use_case": None,
    "team_size": None,
    "timeline": None,
    "meeting_booked": None,
}

company_data_global = None
booked_meetings = []


@function_tool
async def save_lead_field(
    field_name: Annotated[str, "The lead field name: name, company, email, role, use_case, team_size, or timeline"],
    field_value: Annotated[str, "The value provided by the user"],
):
    """Save a lead field when the user provides information during the conversation"""
    if field_name in lead_storage:
        lead_storage[field_name] = field_value
        logger.info(f"Saved lead field: {field_name} = {field_value}")
        return f"Got it, I've noted that down."
    return "Thank you for that information."


@function_tool
async def search_faq(
    question_keywords: Annotated[str, "Keywords or topic from the user's question to search in FAQ"],
):
    """Search the FAQ knowledge base to find relevant information about XpressBees services, pricing, or policies"""
    global company_data_global
    
    if not company_data_global:
        return "I apologize, I'm having trouble accessing information right now. Let me connect you with our team."
    
    question_lower = question_keywords.lower()
    
    # Search through FAQs
    for faq in company_data_global["faqs"]:
        faq_text = f"{faq['question']} {faq['answer']}".lower()
        if any(keyword in faq_text for keyword in question_lower.split()):
            return faq["answer"]
    
    # Search through services
    for service_key, service_data in company_data_global["services"].items():
        service_text = f"{service_data['description']} {' '.join(service_data['features'])}".lower()
        if any(keyword in service_text for keyword in question_lower.split()):
            features = ', '.join(service_data['features'][:3])
            return f"{service_data['description']} Key features include: {features}."
    
    # Search pricing info
    for pricing in company_data_global["pricing"]["services_pricing"]:
        if question_lower in pricing["service"].lower():
            return f"{pricing['service']}: {pricing['notes']}"
    
    return "I'd be happy to get you detailed information on that. Could you share your email so our team can send you comprehensive details?"


@function_tool
async def get_available_meeting_slots(
    number_of_slots: Annotated[int, "Number of available slots to show (default 3-5)"] = 4,
):
    """Get available meeting time slots to offer to the user. Call this when user wants to book a demo, meeting, or consultation."""
    global company_data_global
    
    if not company_data_global or "calendar_availability" not in company_data_global:
        return "I'd love to schedule a meeting with you. Could you share your email and our team will send you a calendar link?"
    
    # Get available slots
    available_slots = [
        slot for slot in company_data_global["calendar_availability"]["available_slots"]
        if slot["available"]
    ]
    
    if not available_slots:
        return "I apologize, but all our slots are currently booked. Could you share your email so we can notify you when new slots open up?"
    
    # Get the first N available slots
    slots_to_offer = available_slots[:number_of_slots]
    
    # Format slots for natural speech
    slot_descriptions = []
    for i, slot in enumerate(slots_to_offer, 1):
        slot_descriptions.append(
            f"Option {i}: {slot['day']}, {slot['date']} at {slot['time']}"
        )
    
    response = "I have the following time slots available for a meeting:\n"
    response += "\n".join(slot_descriptions)
    response += "\n\nWhich time works best for you?"
    
    return response


@function_tool
async def book_meeting_slot(
    slot_identifier: Annotated[str, "The slot identifier - either the option number (1, 2, 3), day name (Monday, Thursday), or time (10:00 AM, 2:00 PM)"],
    meeting_type: Annotated[str, "Type of meeting: demo, consultation, or onboarding"] = "demo",
):
    """Book a specific meeting slot for the user. Call this after user chooses a time slot."""
    global company_data_global, lead_storage, booked_meetings
    
    if not company_data_global or "calendar_availability" not in company_data_global:
        return "I apologize, I'm having trouble accessing the calendar. Let me have our team reach out to schedule."
    
    # Find available slots
    available_slots = [
        slot for slot in company_data_global["calendar_availability"]["available_slots"]
        if slot["available"]
    ]
    
    if not available_slots:
        return "I apologize, but that slot is no longer available. Would you like to see other options?"
    
    # Try to match the slot
    selected_slot = None
    identifier_lower = slot_identifier.lower()
    
    # Try matching by option number (1, 2, 3, etc.)
    if identifier_lower.replace("option", "").strip().isdigit():
        option_num = int(identifier_lower.replace("option", "").strip())
        if 1 <= option_num <= len(available_slots):
            selected_slot = available_slots[option_num - 1]
    
    # Try matching by day name
    if not selected_slot:
        for slot in available_slots:
            if identifier_lower in slot["day"].lower():
                selected_slot = slot
                break
    
    # Try matching by time
    if not selected_slot:
        for slot in available_slots:
            if identifier_lower in slot["time"].lower():
                selected_slot = slot
                break
    
    if not selected_slot:
        return f"I couldn't find a slot matching '{slot_identifier}'. Could you please specify the option number or day?"
    
    # Mark slot as booked
    for slot in company_data_global["calendar_availability"]["available_slots"]:
        if slot["id"] == selected_slot["id"]:
            slot["available"] = False
            break
    
    # Create meeting record
    meeting_record = {
        "meeting_id": f"MTG_{random.randint(1000, 9999)}",
        "lead_name": lead_storage.get("name", "Unknown"),
        "lead_email": lead_storage.get("email", "Not provided"),
        "lead_company": lead_storage.get("company", "Not provided"),
        "meeting_type": meeting_type,
        "date": selected_slot["date"],
        "day": selected_slot["day"],
        "time": selected_slot["time"],
        "duration_minutes": selected_slot["duration_minutes"],
        "booked_at": datetime.now().isoformat(),
        "timezone": company_data_global["calendar_availability"]["timezone"],
    }
    
    booked_meetings.append(meeting_record)
    lead_storage["meeting_booked"] = meeting_record
    
    # Save to file immediately
    meetings_dir = Path("meetings")
    meetings_dir.mkdir(exist_ok=True)
    
    meeting_file = meetings_dir / f"{meeting_record['meeting_id']}.json"
    with open(meeting_file, "w", encoding="utf-8") as f:
        json.dump(meeting_record, f, indent=2)
    
    logger.info(f"Meeting booked: {meeting_record}")
    
    # Generate confirmation message
    confirmation = f"Perfect! I've booked a {meeting_type} meeting for you on {selected_slot['day']}, {selected_slot['date']} at {selected_slot['time']} IST. "
    
    if lead_storage.get("email"):
        confirmation += f"You'll receive a confirmation email at {lead_storage['email']} with calendar invite and meeting details. "
    else:
        confirmation += "Could you share your email so I can send you a confirmation with calendar invite? "
    
    confirmation += "Is there anything else I can help you with?"
    
    return confirmation


@function_tool
async def end_conversation_summary():
    """Generate a summary when the user indicates they want to end the conversation. Call this when user says goodbye, thanks, done, that's all, etc."""
    global lead_storage, company_data_global, booked_meetings
    
    # Save lead data to JSON file
    output_dir = Path("leads")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = random.randint(1000, 9999)
    filename = f"lead_{lead_storage.get('name', 'unknown').replace(' ', '_')}_{timestamp}.json"
    filepath = output_dir / filename
    
    # Add metadata
    lead_export = lead_storage.copy()
    lead_export["company_contacted"] = "XpressBees"
    lead_export["conversation_ended_at"] = datetime.now().isoformat()
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(lead_export, f, indent=2)
    
    logger.info(f"Lead data saved to {filepath}")
    logger.info(f"Lead summary: {json.dumps(lead_storage, indent=2)}")
    
    # Generate verbal summary
    summary_parts = []
    
    if lead_storage["name"]:
        summary_parts.append(f"It was great speaking with {lead_storage['name']}")
    
    if lead_storage["company"]:
        summary_parts.append(f"from {lead_storage['company']}")
    
    if lead_storage["use_case"]:
        summary_parts.append(f"You mentioned you're interested in our services for {lead_storage['use_case']}")
    
    if lead_storage["meeting_booked"]:
        meeting = lead_storage["meeting_booked"]
        summary_parts.append(f"We have your meeting scheduled for {meeting['day']}, {meeting['date']} at {meeting['time']}")
    
    if lead_storage["timeline"]:
        summary_parts.append(f"and you're looking to get started {lead_storage['timeline']}")
    
    if any(lead_storage.values()):
        summary = ". ".join(summary_parts) + "."
        closing = f"{summary} Our team will reach out to you shortly. Thank you for considering XpressBees!"
    else:
        closing = "Thank you for connecting with XpressBees today! Feel free to reach out anytime you need logistics support. Have a wonderful day!"
    
    return closing


class XpressBeesSDR(Agent):
    def __init__(self, company_data: dict) -> None:
        global company_data_global
        company_data_global = company_data
        
        # Random greeting
        greeting = random.choice(company_data["greetings"])
        
        # Build comprehensive knowledge context
        knowledge_context = self._build_knowledge_context(company_data)
        
        super().__init__(
            instructions=f"""{greeting}

You are a professional Sales Development Representative (SDR) for XpressBees, India's leading tech-powered logistics company. 
You have a warm, calm, and soothing voice that puts customers at ease.

COMPANY OVERVIEW:
{company_data['company']['description']}

We deliver {company_data['company']['daily_shipment_volume']:,} shipments daily across {company_data['company']['coverage']['pin_codes_covered']:,} pin codes and {company_data['company']['coverage']['cities_covered']}+ cities.

YOUR PERSONALITY:
- Warm, friendly, and professional with a calm demeanor
- Patient and attentive listener who genuinely cares
- Helpful without being pushy or aggressive
- Speak naturally as if having a friendly conversation
- Use simple, clear language that anyone can understand
- Keep responses concise - aim for 2-3 sentences typically
- Never use emojis, asterisks, or complex formatting
- Sound human and relatable, not robotic

YOUR ROLE AS SDR:
1. Greet visitors warmly and make them feel comfortable
2. Ask what brought them to XpressBees and what they're working on
3. Listen actively to understand their logistics needs and challenges
4. Answer questions using the search_faq tool when needed
5. Naturally collect lead information using save_lead_field tool
6. Offer to schedule meetings when appropriate
7. When conversation ends, use end_conversation_summary tool

CONVERSATION APPROACH:
- Start by asking: "What brings you to XpressBees today?" or "What kind of logistics challenges are you facing?"
- Listen to their needs before jumping into features
- Ask clarifying questions to understand their situation better
- Share relevant information based on what they actually need
- Naturally weave in questions like "What company are you with?" or "What's your role there?"
- Don't interrogate - make it conversational and natural
- When they provide information, use save_lead_field to store it

MEETING SCHEDULING:
When user expresses interest in a demo, consultation, or wants to learn more:
1. First ensure you have their NAME and EMAIL (required for booking)
2. Use get_available_meeting_slots tool to show available times
3. Present 3-4 options naturally: "I have Thursday at 10 AM, Thursday at 2 PM, or Friday at 11 AM available"
4. When they choose, use book_meeting_slot tool with their choice
5. Confirm the booking details clearly
6. Meeting types: demo (product demo), consultation (business discussion), onboarding (getting started)

INFORMATION TO COLLECT (naturally during conversation):
- name: Their full name (REQUIRED for booking meetings)
- company: Company name they work for
- email: Email address for follow-up (REQUIRED for booking meetings)
- role: Their role/position
- use_case: What they want to use logistics services for
- team_size: Size of their team/operation
- timeline: When they want to start (immediately, soon, or later)

WHEN USER WANTS TO END:
If user says anything like "that's all", "thanks", "goodbye", "I'm done", "that's it", etc., 
immediately call the end_conversation_summary tool to wrap up professionally.

{knowledge_context}

Remember: You're here to help solve their logistics problems and build a relationship, not just collect data. 
Be genuinely curious about their business and challenges. Speak naturally like a helpful human, not a scripted bot.""",
            tools=[save_lead_field, search_faq, get_available_meeting_slots, book_meeting_slot, end_conversation_summary],
        )

    def _build_knowledge_context(self, data: dict) -> str:
        """Build knowledge context for the agent"""
        context = "\n=== SERVICES WE OFFER ===\n"
        
        for service_key, service_data in data["services"].items():
            context += f"\n{service_key.upper().replace('_', ' ')}:\n"
            context += f"{service_data['description']}\n"
            context += f"Features: {', '.join(service_data['features'])}\n"
        
        context += "\n=== KEY INFORMATION ===\n"
        context += f"Coverage: {data['company']['coverage']['pin_codes_covered']:,} pin codes, {data['company']['coverage']['cities_covered']}+ cities\n"
        context += f"Daily Volume: {data['company']['daily_shipment_volume']:,} shipments\n"
        context += f"Industries: {', '.join(data['company']['industries_served'])}\n"
        
        context += "\n=== PRICING APPROACH ===\n"
        context += data['pricing']['general_info'] + "\n"
        context += "We offer customized quotes based on volume and needs.\n"
        
        context += "\n=== WHEN TO USE TOOLS ===\n"
        context += "- Use search_faq tool when user asks specific questions about services, pricing, coverage, or features\n"
        context += "- Use save_lead_field tool when user provides their name, company, email, role, use case, team size, or timeline\n"
        context += "- Use get_available_meeting_slots tool when user wants to book a demo, meeting, or consultation\n"
        context += "- Use book_meeting_slot tool when user selects a specific time slot\n"
        context += "- Use end_conversation_summary tool when user wants to end the conversation\n"
        
        return context


def prewarm(proc: JobProcess):
    """Prewarm VAD and load company data"""
    proc.userdata["vad"] = silero.VAD.load()
    
    # Load company data using absolute path
    current_dir = Path(__file__).parent
    details_path = current_dir / "details.json"
    
    logger.info(f"Loading company data from: {details_path}")
    
    if not details_path.exists():
        logger.error(f"details.json not found at {details_path}")
        raise FileNotFoundError(f"details.json not found at {details_path}")
    
    with open(details_path, "r", encoding="utf-8") as f:
        proc.userdata["company_data"] = json.load(f)
    
    logger.info("Company data loaded and VAD prewarmed successfully")


async def entrypoint(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Get company data from prewarm
    company_data = ctx.proc.userdata["company_data"]

    # Set up voice AI pipeline with calm, soothing voice
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="Ronnie",  # Warm, professional male voice
            style="Conversational", 
            model="Falcon",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Create SDR agent with company data
    sdr_agent = XpressBeesSDR(company_data)

    await session.start(
        agent=sdr_agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))