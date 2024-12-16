import asyncio
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import subprocess
import sys

class DroneDispatchRequest(Model):
    target_city: str

class HumanDetectionRequest(Model):
    folder_path: str  # Path to the folder containing images

bob = Agent(
    name="bob",
    port=8003,
    seed="bob's unique seed phrase",
    endpoint=["http://127.0.0.1:8003/submit"],
)

# Define the human detection agent address
HUMAN_DETECTION_AGENT_ADDRESS = "agent1qdykgdgrrm5en7tzqv0v6cjy7s0ujunjlp5qwgh93qu70mfx70pxkwruza9"  # Replace with the actual address of the human detection agent

@bob.on_event("startup")
async def introduce(ctx: Context):
    ctx.logger.info(f"Bob's address: {ctx.address}")
    await fund_agent_if_low(ctx.wallet.address())

@bob.on_message(model=DroneDispatchRequest)
async def handle_dispatch_request(ctx: Context, sender: str, msg: DroneDispatchRequest):
    ctx.logger.info(f"Received dispatch request from {sender} for location: {msg.target_city}")
    
    dispatch_message = f"Drone has been dispatched to {msg.target_city}"
    ctx.logger.info(dispatch_message)
    
    # Trigger the human detection agent after dispatch
    ctx.logger.info(f"Triggering human detection agent for image analysis in the folder.")
    
    # You can change the folder path to where your images are located
    human_detection_request = HumanDetectionRequest(folder_path="valid/images")
    await ctx.send(HUMAN_DETECTION_AGENT_ADDRESS, human_detection_request)
    
    # Run the drone dispatch simulation in a separate process
    process = subprocess.Popen([sys.executable, "drone_simulation.py", msg.target_city], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)
    
    # Wait for the process to complete
    stdout, stderr = process.communicate()
    
    if process.returncode == 0:
        simulation_result = stdout.strip()
        ctx.logger.info(f"Drone dispatched successfully to {msg.target_city}. Simulation Result: {simulation_result}")
    else:
        error_message = f"Simulation failed: {stderr}"
        ctx.logger.error(error_message)

if __name__ == "__main__":
    bob.run()
