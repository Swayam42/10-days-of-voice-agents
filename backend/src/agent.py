import logging
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
from database import FraudDatabase

logger = logging.getLogger("agent")
load_dotenv(".env.local")

# Initialize database
fraud_db = FraudDatabase()

class BharatFraudAlertAssistant(Agent):
    def __init__(self) -> None:
        # Store conversation state
        self.current_case = None
        self.verification_passed = False
        self.call_stage = "greeting"  # greeting, username_collection, verification, transaction_review, completion
        self.username_attempted = False
        
        super().__init__(
            instructions="""You are Rajesh Kumar, a fraud detection officer at Bharat Secure Bank, one of India's most trusted banks. You speak with a professional yet warm Indian tone.

Your mission is to investigate suspicious transactions and protect customers. Follow this EXACT flow:

**STAGE 1 - GREETING:**
Say: "Namaste! This is Rajesh Kumar from Bharat Secure Bank Fraud Prevention Department. We have detected a suspicious transaction on your account which requires immediate verification. This call is being recorded for quality and security purposes."

**STAGE 2 - USERNAME COLLECTION:**
Ask: "May I please have your full name as registered with the bank?"
Once they provide their name, use the get_fraud_case tool with their exact name.

**STAGE 3 - VERIFICATION:**
After retrieving the case, ask them the security question from their file.
Listen carefully to their answer and use the verify_security_answer tool.

If verification FAILS:
- Say: "I am sorry sir, but the security answer does not match our records. For your safety, I cannot proceed with this call. Please visit your nearest branch with valid ID proof or call our official customer care number. Thank you."
- End the conversation politely.

**STAGE 4 - TRANSACTION DETAILS (only if verified):**
Say: "Thank you for verifying your identity. Now, we have detected a suspicious transaction on your card. Let me read out the details."

Then clearly state:
"A transaction of rupees [amount] was attempted at [merchant name] in [location] on [date and time]. This transaction was on your card ending in [last 4 digits]."

**STAGE 5 - CONFIRMATION:**
Ask directly: "Sir, did you authorize this transaction? Please say yes or no."

**STAGE 6 - ACTION:**
Listen carefully to their response:

If they say YES or confirm:
- Use mark_transaction_safe tool
- Say: "Thank you for confirming sir. We have marked this transaction as legitimate in our system. Your card will continue working normally. Is there anything else I can help you with?"

If they say NO or deny:
- Use mark_transaction_fraudulent tool  
- Say: "I understand your concern sir. We have immediately blocked this transaction and your card for security purposes. A new card will be dispatched to your registered address within 3 to 5 working days. We will also initiate a fraud investigation. You will receive an SMS confirmation shortly. Is there anything else you need assistance with?"

**STAGE 7 - CLOSING:**
Say: "Thank you for your time and cooperation sir. Have a great day ahead!"

**IMPORTANT GUIDELINES:**
- Use "sir" or "madam" respectfully when addressing the customer
- Speak naturally in Indian English style
- Keep responses conversational and clear
- Never use asterisks, emojis, or complex formatting
- Always be polite and patient
- If customer seems confused, repeat information clearly
- Use rupees instead of dollars
- Maintain professional but friendly tone throughout""",
        )
    
    @function_tool
    async def get_fraud_case(self, context: RunContext, username: str):
        """Retrieve a fraud case from the database by customer name.
        
        This tool loads the pending fraud case for the given customer and prepares
        the security question for verification.
        
        Args:
            username: The customer's full name as registered with the bank
        """
        logger.info(f"Looking up fraud case for: {username}")
        
        # Clean up the username
        username = username.strip()
        
        case = fraud_db.get_fraud_case_by_username(username)
        
        if case:
            self.current_case = case
            self.username_attempted = True
            self.call_stage = "verification"
            logger.info(f"Found fraud case ID {case['id']} for {username}")
            logger.info(f"   Card: ****{case['cardEnding']}")
            logger.info(f"   Amount: ₹{case['transactionAmount']:,.2f}")
            logger.info(f"   Merchant: {case['transactionName']}")
            
            return f"""Found pending fraud case for {username}.

CASE DETAILS:
- Customer ID: {case['securityIdentifier']}
- Card Ending: {case['cardEnding']}
- Transaction Amount: ₹{case['transactionAmount']}
- Merchant: {case['transactionName']}
- Location: {case['transactionLocation']}
- Date and Time: {case['transactionTime']}
- Category: {case['transactionCategory']}

SECURITY VERIFICATION REQUIRED:
Ask this question: {case['securityQuestion']}

Proceed to verification stage."""
        else:
            logger.warning(f"No pending fraud case found for: {username}")
            return f"No pending fraud cases found for {username}. The customer may have provided an incorrect name, or all their cases are already resolved. Ask them to confirm their registered name or inform them there are no pending alerts."
    
    @function_tool
    async def verify_security_answer(self, context: RunContext, customer_answer: str):
        """Verify the customer's answer to the security question.
        
        This tool checks if the provided answer matches the expected answer in the database.
        Verification must pass before discussing transaction details.
        
        Args:
            customer_answer: The answer provided by the customer to the security question
        """
        if not self.current_case:
            logger.warning("Verification attempted without active case")
            return "No active fraud case to verify. Please retrieve a case first using get_fraud_case."
        
        correct_answer = self.current_case['securityAnswer'].lower().strip()
        provided_answer = customer_answer.lower().strip()
        
        logger.info(f"Security Verification:")
        logger.info(f"   Expected: {correct_answer}")
        logger.info(f"   Received: {provided_answer}")
        
        # Allow partial matching for common variations
        if provided_answer == correct_answer or correct_answer in provided_answer or provided_answer in correct_answer:
            self.verification_passed = True
            self.call_stage = "transaction_review"
            logger.info("Verification SUCCESSFUL")
            return "Security verification successful. Customer identity confirmed. You may now proceed to discuss the transaction details with the customer."
        else:
            self.verification_passed = False
            self.call_stage = "verification_failed"
            
            # IMPORTANT: Update database immediately when verification fails
            case_id = self.current_case['id']
            customer_name = self.current_case['userName']
            
            fraud_db.update_fraud_case_status(
                case_id=case_id,
                status="verification_failed",
                outcome_note=f"Customer {customer_name} failed security verification. Provided incorrect answer to security question. Call terminated for security."
            )
            
            logger.warning("Verification FAILED - Database updated")
            logger.info(f"CASE {case_id} MARKED AS VERIFICATION_FAILED")
            
            return "Security verification FAILED. The answer does not match our records. Database has been updated with verification failure. You MUST end the call immediately for security reasons. Do not proceed with transaction discussion."
    
    @function_tool
    async def mark_transaction_safe(self, context: RunContext):
        """Mark the current transaction as safe because the customer confirmed they made it.
        
        This tool updates the database to indicate the customer authorized the transaction.
        Use this when the customer says YES or confirms the transaction.
        """
        if not self.current_case:
            logger.warning("Attempted to mark safe without active case")
            return "No active fraud case to update. Cannot mark as safe."
        
        if not self.verification_passed:
            logger.error("Attempted to mark safe without verification")
            return "Customer verification did not pass. Cannot update case status. Call must end."
        
        case_id = self.current_case['id']
        customer_name = self.current_case['userName']
        
        fraud_db.update_fraud_case_status(
            case_id=case_id,
            status="confirmed_safe",
            outcome_note=f"Customer {customer_name} confirmed the transaction as legitimate. No fraud detected."
        )
        
        self.call_stage = "completion"
        logger.info(f"CASE {case_id} MARKED AS SAFE")
        logger.info(f"   Customer: {customer_name}")
        logger.info(f"   Outcome: Transaction confirmed legitimate")
        
        return f"Transaction successfully marked as SAFE in the system. Case closed. Customer {customer_name} confirmed they made this transaction."
    
    @function_tool
    async def mark_transaction_fraudulent(self, context: RunContext):
        """Mark the current transaction as fraudulent because the customer did not make it.
        
        This tool updates the database to indicate fraud was detected and the card is blocked.
        Use this when the customer says NO or denies making the transaction.
        """
        if not self.current_case:
            logger.warning("Attempted to mark fraudulent without active case")
            return "No active fraud case to update. Cannot mark as fraudulent."
        
        if not self.verification_passed:
            logger.error("Attempted to mark fraudulent without verification")
            return "Customer verification did not pass. Cannot update case status. Call must end."
        
        case_id = self.current_case['id']
        customer_name = self.current_case['userName']
        card_ending = self.current_case['cardEnding']
        amount = self.current_case['transactionAmount']
        
        fraud_db.update_fraud_case_status(
            case_id=case_id,
            status="confirmed_fraud",
            outcome_note=f"Customer {customer_name} denied making the transaction of ₹{amount}. Card ****{card_ending} blocked. Fraud investigation initiated."
        )
        
        self.call_stage = "completion"
        logger.info(f"CASE {case_id} MARKED AS FRAUDULENT")
        logger.info(f"   Customer: {customer_name}")
        logger.info(f"   Card Blocked: ****{card_ending}")
        logger.info(f"   Amount: ₹{amount:,.2f}")
        logger.info(f"   Outcome: Fraud confirmed, card blocked, new card dispatched")
        
        return f"Transaction marked as FRAUDULENT. Card ****{card_ending} has been blocked immediately. New card dispatch initiated. Fraud investigation case opened for ₹{amount}."


def prewarm(proc: JobProcess):
    """Prewarm the VAD model for faster startup"""
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("VAD model prewarmed")


async def entrypoint(ctx: JobContext):
    """Main entrypoint for the Bharat Secure Bank Fraud Alert Agent"""
    
    # Check if this is a phone call (telephony) or browser call
    is_phone_call = ctx.room.name.startswith("fraud-call-") or "sip" in ctx.room.name.lower()
    call_source = "Phone (Telephony)" if is_phone_call else "Browser (WebRTC)"
    
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "bank": "Bharat Secure Bank",
        "call_source": call_source
    }
    
    logger.info("="*70)
    logger.info(f"Starting Bharat Secure Bank Fraud Alert Agent...")
    logger.info(f"Call Source: {call_source}")
    logger.info(f"Room Name: {ctx.room.name}")
    logger.info("="*70)
    
    # Set up voice AI pipeline optimized for both phone and browser calls
    # Phone calls require clearer speech and more reliable transcription
    session = AgentSession(
        # Speech-to-text optimized for Indian accents
        stt=deepgram.STT(
            model="nova-3",
            language="en-IN",  # Indian English
            # Phone calls typically use 8kHz-16kHz audio
            sample_rate=16000 if is_phone_call else 48000,
        ),
        
        # LLM for intelligent conversation handling
        llm=google.LLM(
            model="gemini-2.5-flash",
            # Slightly more consistent responses for phone calls
            temperature=0.6 if is_phone_call else 0.7,
        ),
        
        # Text-to-speech with professional voice
        tts=murf.TTS(
            voice="Ronnie",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
            # Phone calls benefit from slightly slower, clearer speech
            speed=0.95 if is_phone_call else 1.0,
        ),
        
        # Turn detection for natural conversation flow
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        
        # Enable preemptive generation for faster responses
        preemptive_generation=True,
    )
    
    # Metrics collection for monitoring
    usage_collector = metrics.UsageCollector()
    
    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)
    
    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Session Usage Summary: {summary}")
    
    ctx.add_shutdown_callback(log_usage)
    
    # Start the agent session
    logger.info("Initializing voice pipeline...")
    
    # Create agent instance so we can track its state
    fraud_agent = BharatFraudAlertAssistant()
    
    # Add cleanup callback to ensure database is updated if call drops
    async def cleanup_on_disconnect():
        """Ensure database is updated even if call drops unexpectedly"""
        logger.info("Call ending - checking for pending database updates...")
        
        if fraud_agent.current_case and fraud_agent.call_stage != "completion":
            case_id = fraud_agent.current_case['id']
            customer_name = fraud_agent.current_case['userName']
            
            # If we got to verification but didn't complete
            if fraud_agent.call_stage in ["verification", "transaction_review"] and not fraud_agent.verification_passed:
                fraud_db.update_fraud_case_status(
                    case_id=case_id,
                    status="call_incomplete",
                    outcome_note=f"Call with {customer_name} ended before completion. Stage: {fraud_agent.call_stage}. No final decision recorded."
                )
                logger.warning(f"CASE {case_id} MARKED AS INCOMPLETE - Call dropped at {fraud_agent.call_stage} stage")
            
            elif fraud_agent.call_stage == "verification_failed":
                # Already updated in verify_security_answer
                logger.info(f"CASE {case_id} already marked as verification_failed")
            
            elif fraud_agent.call_stage == "completion":
                # Already updated in mark_transaction_safe/fraudulent
                logger.info(f"CASE {case_id} already marked as completed")
        
        logger.info("Cleanup complete")
    
    ctx.add_shutdown_callback(cleanup_on_disconnect)
    
    await session.start(
        agent=fraud_agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # Noise cancellation for clear audio (important for phone calls)
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    # Connect to the room
    logger.info("Connecting to room...")
    await ctx.connect()
    logger.info("Agent connected and ready!")
    logger.info("="*70)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm,
        agent_name="fraud-alert-agent"  # Must match dispatch rule in LiveKit Cloud!
    ))