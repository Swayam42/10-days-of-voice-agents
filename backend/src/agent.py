import logging
import random
from typing import Optional, Annotated
from enum import Enum
from dataclasses import dataclass, field
import uuid
from datetime import datetime

from dotenv import load_dotenv
from pydantic import Field
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    cli,
    function_tool,
    RunContext,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# -------------------------
# Logging
# -------------------------
logger = logging.getLogger("improv_battle_agent")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
if not logger.handlers:
    logger.addHandler(handler)

load_dotenv(".env.local")

# -------------------------
# Game state and scenarios
# -------------------------
class GamePhase(Enum):
    INTRO = "intro"
    EXPLAINING_RULES = "explaining_rules"
    SCENARIO_ANNOUNCE = "scenario_announce"
    AWAITING_IMPROV = "awaiting_improv"
    REACTING = "reacting"
    DONE = "done"


IMPROV_SCENARIOS = [
    "You're a chai seller trying to convince a customer to try your new crazy flavor - pizza chai.",
    "You're a street vendor trying to sell an ordinary pen like it's the most amazing thing ever invented.",
    "You're negotiating the price at a local market, and the shopkeeper is your long-lost school friend.",
    "You're explaining to your mom why you need to order food again when there's already food at home.",
    "You're calling your friend to cancel plans because you're too lazy to leave the house, but you need a convincing excuse.",
]


@dataclass
class ImprovBattleState:
    player_name: Optional[str] = None
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    current_round: int = 0  # number of rounds presented so far (0..max_rounds)
    max_rounds: int = 3
    rounds: list = field(default_factory=list)  # Each: {"round": int, "scenario": str, "host_reaction": str}
    phase: GamePhase = GamePhase.INTRO
    selected_scenarios: list = field(default_factory=list)
    current_scenario: Optional[str] = None
    rules_explained: bool = False
    used_indices: list = field(default_factory=list)


def _pick_scenario(state: ImprovBattleState) -> str:
    candidates = [i for i in range(len(IMPROV_SCENARIOS)) if i not in state.used_indices]
    if not candidates:
        state.used_indices = []
        candidates = list(range(len(IMPROV_SCENARIOS)))
    idx = random.choice(candidates)
    state.used_indices.append(idx)
    return IMPROV_SCENARIOS[idx]


# -------------------------
# Tools
# -------------------------
@function_tool
async def explain_game_rules(
    ctx: RunContext[ImprovBattleState],
    player_name: Annotated[Optional[str], Field(description="Optional player name", default=None)] = None,
) -> str:
    state = ctx.userdata
    if player_name and not state.player_name:
        state.player_name = player_name.strip()
        logger.info(f"Set player name: {state.player_name}")

    if not state.player_name:
        state.player_name = "friend"

    state.phase = GamePhase.EXPLAINING_RULES
    state.rules_explained = True
    logger.info("Rules explained")

    return (
        f"Perfect, {state.player_name}! Here's how Improv Battle works. "
        f"I will give you {state.max_rounds} short scenarios. For each, act it out for about 20–30 seconds and then say 'End scene' or pause. "
        "I'll react briefly after each scene. Ready to jump into scene 1?"
    )


@function_tool
async def start_game(ctx: RunContext[ImprovBattleState]) -> str:
    state = ctx.userdata
    if not state.rules_explained:
        return "Hold on — let me explain the rules first."

    state.phase = GamePhase.SCENARIO_ANNOUNCE
    state.current_round = 0
    state.selected_scenarios = [ _pick_scenario(state) for _ in range(state.max_rounds) ]
    logger.info(f"Game started for {state.player_name}: preselected {len(state.selected_scenarios)} scenarios")
    return f"Awesome! Let's do this, {state.player_name}! I'll present the first scene now."


@function_tool(description="Present the next improv scenario to the player. ONLY call this when the user confirms they're ready for the next scene (e.g., says 'yes', 'next', 'ready'). Do NOT call immediately after react_to_improv.")
async def present_scenario(ctx: RunContext[ImprovBattleState]) -> str:
    state = ctx.userdata

    if state.phase == GamePhase.DONE:
        return "The game is over. Say 'start' to play again."

    if state.current_round >= state.max_rounds:
        state.phase = GamePhase.DONE
        return "All scenarios have already been presented."

    # Present scenario at index current_round, then increment to indicate it's been presented
    scenario = state.selected_scenarios[state.current_round]
    state.current_scenario = scenario
    state.current_round += 1  # now represents number of rounds presented
    state.phase = GamePhase.AWAITING_IMPROV

    logger.info(f"Presented round {state.current_round}/{state.max_rounds}: {scenario}")
    return f"Alright, scene {state.current_round}! {scenario} Go ahead — improvise now and say 'End scene' when you're done."


@function_tool(description="Give feedback on the player's improv performance after they complete a scene. Call this ONLY after the user has finished performing (said 'end scene' or finished talking). After calling this, wait for the user to confirm they want the next scene before calling present_scenario again.")
async def react_to_improv(
    ctx: RunContext[ImprovBattleState],
    performance_summary: Annotated[str, Field(description="Brief summary of player performance")],
) -> str:
    state = ctx.userdata

    # current_round represents number of scenarios presented, so the completed round is current_round
    completed_round = state.current_round
    if completed_round == 0:
        # defensive: no round has been presented
        logger.warning("react_to_improv called but no round presented yet")
        return "I haven't given a scene yet — say 'start' to begin."

    logger.info(f"Reacting to round {completed_round} performance. Rounds stored so far: {len(state.rounds)}")

    # build varied reactions
    enthusiastic = [
        f"Wow, {state.player_name}! That was hilarious — brilliant commitment to the bit!",
        f"That really landed! The specific details were gold, well done!",
        f"Incredible — you leaned into it and it paid off!",
    ]
    positive = [
        f"Nice work, {state.player_name}. You stayed in character and had good energy.",
        f"That was solid! A few sharper specifics and it would pop even more.",
        f"Good instincts — keep pushing the choices next time.",
    ]
    constructive = [
        f"Good start! Try to make one clear choice and deepen it a bit.",
        f"Not bad — the setup was there, but the payoff could be clearer.",
        f"Solid attempt. If you exaggerate one detail, it will sell stronger.",
    ]

    reaction = random.choice(enthusiastic + positive + constructive)

    state.rounds.append({
        "round": completed_round,
        "scenario": state.current_scenario,
        "host_reaction": reaction,
        "performance": performance_summary,
    })

    state.phase = GamePhase.REACTING
    logger.info(f"Stored performance for round {completed_round}. Rounds stored: {len(state.rounds)}")

    # If we've completed all rounds, return the full closing with gift message
    if state.current_round >= state.max_rounds:
        state.phase = GamePhase.DONE
        logger.info("All rounds complete — ending game automatically")
        
        closing = f"{reaction} And that's a wrap, {state.player_name}! "
        closing += f"You completed all {state.max_rounds} rounds. "
        if len(state.rounds) >= 2:
            memorable = state.rounds[1]["scenario"] if len(state.rounds) > 1 else state.rounds[0]["scenario"]
            closing += f"My favorite was the '{memorable[:60]}' scene. "
        
        closing += "You've got solid improv instincts — keep committing to big choices. "
        closing += "And now for what you've been waiting for — your special gift! Check your screen and click the gift box to claim it. Thanks for playing Improv Battle!"
        
        return closing
    else:
        # Prepare for the next scenario but DO NOT present it automatically
        state.phase = GamePhase.SCENARIO_ANNOUNCE
        logger.info(f"More rounds remain — waiting for user to request next scenario. Current round: {state.current_round}, Stored rounds: {len(state.rounds)}")
        return f"{reaction} That was round {completed_round}! Ready for the next challenge? Say 'yes' or 'next' when you're ready!"


@function_tool
async def end_game(ctx: RunContext[ImprovBattleState]) -> str:
    state = ctx.userdata
    logger.info(f"end_game called. current_round={state.current_round}, max_rounds={state.max_rounds}")

    if state.current_round < state.max_rounds:
        logger.error("end_game called prematurely")
        # current_round is number of rounds presented so far (0..max_rounds)
        return f"Hold up — we've only completed {len(state.rounds)} of {state.max_rounds} rounds. Let's finish the game first."

    state.phase = GamePhase.DONE

    closing = f"And that's a wrap, {state.player_name}! "
    if state.rounds:
        closing += f"You completed {len(state.rounds)} rounds. "
        if len(state.rounds) >= 2:
            memorable = state.rounds[1]["scenario"] if len(state.rounds) > 1 else state.rounds[0]["scenario"]
            closing += f"My favorite was the '{memorable[:60]}' scene. "

    closing += "You've got solid improv instincts — keep committing to big choices. "
    closing += "And now for what you've been waiting for — your special gift! Check your screen and click the gift box to claim it. Thanks for playing Improv Battle!"

    logger.info("Game ended, returning closing summary")
    return closing


@function_tool
async def get_game_status(ctx: RunContext[ImprovBattleState]) -> str:
    state = ctx.userdata
    if not state.player_name:
        return "Game not started. Tell me your name to begin!"

    # current_round is the number of rounds presented so far; show next round index (human-friendly)
    next_round = min(state.current_round + 1, state.max_rounds) if state.current_round < state.max_rounds else state.max_rounds
    status = (
        f"Player: {state.player_name}\n"
        f"Presented rounds: {state.current_round}/{state.max_rounds}\n"
        f"Phase: {state.phase.value}\n"
        f"Rules explained: {state.rules_explained}\n"
    )
    return status


@function_tool
async def stop_game(ctx: RunContext[ImprovBattleState]) -> str:
    state = ctx.userdata
    state.phase = GamePhase.DONE
    logger.info(f"Game stopped early. Rounds completed: {len(state.rounds)}/{state.max_rounds}")
    if len(state.rounds) == 0:
        return f"No problem, {state.player_name or 'friend'}! Thanks for stopping by Improv Battle. Come back anytime!"
    else:
        return f"Got it — you completed {len(state.rounds)} round{'s' if len(state.rounds) != 1 else ''}. Thanks for playing Improv Battle!"


# -------------------------
# Agent
# -------------------------
class ImprovHostAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            tools=[explain_game_rules, start_game, present_scenario, react_to_improv, end_game, get_game_status, stop_game],
            instructions="""
You are the host of Improv Battle. Keep responses short (1-3 sentences), TTS-friendly, and use the tools to manage flow.
Follow the 3-round sequence: explain_game_rules -> start_game -> present_scenario -> react_to_improv -> present_scenario -> react_to_improv -> present_scenario -> react_to_improv -> end_game.
"""
        )

    async def on_user_turn_completed(self, turn_ctx, new_message) -> None:
        state = self.session.userdata
        user_text = new_message.text_content if isinstance(new_message.text_content, str) else str(new_message.content)
        user_text_lower = user_text.lower()

        scene_end_phrases = ["end scene", "that's it", "i'm done", "scene end", "scene over"]
        if any(phrase in user_text_lower for phrase in scene_end_phrases):
            logger.info("Explicit scene end detected")

        exit_phrases = ["stop game", "end game", "quit", "exit", "i want to leave", "stop the game"]
        if any(phrase in user_text_lower for phrase in exit_phrases):
            logger.info("Early exit intent detected")

        logger.info(f"User turn completed. Phase: {state.phase.value}, Round: {state.current_round}/{state.max_rounds}")
        logger.info(f"User said (snippet): {user_text[:120]}")


    async def on_session_start(self, session: AgentSession) -> None:
        # Wait for at least one remote participant to appear, but proceed gracefully if none
        try:
            await session.wait_for_user(timeout_seconds=6)
        except Exception:
            # proceed; we will ask for name if not available
            logger.info("wait_for_user timed out or not available; continuing")

        participants = list(session.room.remote_participants.values())
        player_name = None

        if participants:
            p = participants[0]
            if getattr(p, "name", None):
                player_name = p.name.strip()
            elif getattr(p, "identity", None) and not p.identity.startswith("voice_assistant_user_"):
                player_name = p.identity

        state = session.userdata
        if player_name:
            state.player_name = player_name
            state.phase = GamePhase.INTRO
            await session.say(
                f"Hey {player_name}! Welcome to Improv Battle - the voice improv game show! Want me to explain how it works?",
                add_to_chat_ctx=True,
            )
            logger.info(f"Session started with player: {player_name}")
        else:
            state.phase = GamePhase.INTRO
            await session.say(
                "Hey there! Welcome to Improv Battle - the voice improv game show! What's your name?",
                add_to_chat_ctx=True,
            )
            logger.warning("No participant name; prompted for name")


# -------------------------
# Entrypoint & Prewarm
# -------------------------
def prewarm(proc: JobProcess):
    try:
        proc.userdata["vad"] = silero.VAD.load()
        logger.info("VAD preloaded")
    except Exception:
        logger.warning("VAD prewarm failed; continuing without preloaded VAD")
        proc.userdata["vad"] = None


async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}
    userdata = ImprovBattleState()

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="Matthew",
            style="Conversational",
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata.get("vad"),
        preemptive_generation=True,
        userdata=userdata,
    )

    agent = ImprovHostAssistant()
    await session.start(
        agent=agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
