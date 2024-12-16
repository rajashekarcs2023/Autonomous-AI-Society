from uagents import Agent, Context, Model

# Initialize the trigger agent
trigger_agent = Agent(
    name="trigger_agent",
    port=8006,
    seed="trigger_agent_secret_seed",
    endpoint=["http://127.0.0.1:8006/submit"],
)

class HumanDetectionRequest(Model):
    folder_path: str  # Path to the folder containing images

@trigger_agent.on_event("startup")
async def startup_event(ctx: Context):
    ctx.logger.info(f"Trigger Agent started at address {ctx.address}")

    # Address of the human detection agent
    human_detection_agent_address = "agent1qdykgdgrrm5en7tzqv0v6cjy7s0ujunjlp5qwgh93qu70mfx70pxkwruza9"
    
    # Send a request to the human detection agent to start processing
    await ctx.send(
        human_detection_agent_address,
        HumanDetectionRequest(folder_path="valid/images")
    )

    # Log that the request was sent, without expecting a response
    ctx.logger.info("Request sent to Human Detection Agent to process images.")

if __name__ == "__main__":
    trigger_agent.run()
