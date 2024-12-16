from uagents import Agent, Context, Model

# Define the agent that will trigger the call_rescue_agent
trigger_agent = Agent(
    name="trigger_agent",
    port=8007,
    seed="trigger_secret_seed",
    endpoint=["http://127.0.0.1:8007/submit"],
)

# Define the model for the message that will be sent to call_rescue_agent
class CallRescueRequest(Model):
    message: str  # The full message containing rescue details

# Address of the call_rescue_agent
CALL_RESCUE_AGENT_ADDRESS = "agent1qv306rfgyvyhpyfdwavl625lh4383kchky39rkqdcz0s7s7t93yjglrjxrr"

@trigger_agent.on_event("startup")
async def introduce(ctx: Context):
    ctx.logger.info(f"Trigger Agent is starting. Address: {ctx.address}")
    print(f"Trigger Agent Address: {ctx.address}")

    # Compose the message that will be sent to the call_rescue_agent
    rescue_message = """
    There is a child trapped on the roof of a house, surrounded by floodwaters. The rescue team needs to reach coordinates (latitude: 25.50798, longitude: -84.19412).
    The water level is rising, and the child is in immediate danger.
    """

    # Send the message to the call_rescue_agent
    call_rescue_request = CallRescueRequest(message=rescue_message)
    await ctx.send(CALL_RESCUE_AGENT_ADDRESS, call_rescue_request)

if __name__ == "__main__":
    trigger_agent.run()
