from uagents import Agent, Context, Model

# Define the distress analysis request model
class DistressAnalysisRequest(Model):
    duration: int

# Create the request sender agent
request_sender = Agent(
    name="request_sender",
    port=8001,
    seed="request_sender_secret_seed",
    endpoint=["http://127.0.0.1:8001/submit"],
)

# Address of the distress analyzer agent (ensure this is correct)
DISTRESS_ANALYZER_ADDRESS = "agent1qg6s5cjun8kz0hz3jaslly0f3nlvmytvn6dmdc8xr2p7mjdpktpsw5ugy3g"

# Log the agent's address when it starts
@request_sender.on_event("startup")
async def introduce(ctx: Context):
    ctx.logger.info(f"Request Sender's address: {ctx.address}")
    # Sending a single distress analysis request upon startup (you can trigger it as per your workflow)
    await send_distress_analysis_request(ctx)

# Function to send a distress analysis request to the distress analyzer
async def send_distress_analysis_request(ctx: Context):
    ctx.logger.info(f"Sending distress analysis request to {DISTRESS_ANALYZER_ADDRESS}")
    request = DistressAnalysisRequest(duration=5)  # Example: request for 5 seconds of audio analysis
    await ctx.send(DISTRESS_ANALYZER_ADDRESS, request)
    ctx.logger.info("Distress analysis request sent")

if __name__ == "__main__":
    request_sender.run()
