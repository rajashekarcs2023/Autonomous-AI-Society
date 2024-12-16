import requests
from uagents import Agent, Context, Model

# Define the call rescue agent
call_rescue_agent = Agent(
    name="call_rescue_agent",
    port=8009,
    seed="call_rescue_secret_seed",
    endpoint=["http://127.0.0.1:8009/submit"],
)

# Define the model for call rescue request
class CallRescueRequest(Model):
    message: str  # The full message containing rescue details

# Function to call Hyperbolic LLaMA API
def call_llama_vision_for_summary(message):
    url = "https://api.hyperbolic.xyz/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": ""  # Add your API key here
    }
    
    data = {
        "messages": [
            {
                "role": "system",
                "content": "You are an assistant to disaster rescue team. From the message given, make a concise summary of the details and surroundings of the person mentioned in the message and also their coordinates.Don't begin with 'The summary is..', just directly gibve the message."
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.9
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get('choices', [{}])[0].get('message', {}).get('content', 'No summary available')
    else:
        return "Error: Failed to summarize the message"

# Function to create the Vapi call
def create_vapi_call(first_message):
    # Hardcoded Vapi API Authorization token and customer number
    auth_token = ''
    
    # The Phone Number ID, and the Customer details for the call
    phone_number_id = ''
    customer_number = ""

    # Create the header with Authorization token
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }

    # Create the data payload for the API request
    data = {
        'assistant': {
            "firstMessage": first_message,
            "model": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a disaster response assistant and will give instructions to the rescue team by providing the details of the people to rescue and the coordinates."
                    }
                ]
            },
            "voice": "jennifer-playht"
        },
        'phoneNumberId': phone_number_id,
        'customer': {
            'number': customer_number,
        },
    }

    # Make the POST request to Vapi to create the phone call
    response = requests.post(
        'https://api.vapi.ai/call/phone', headers=headers, json=data)

    # Check if the request was successful and return the response
    if response.status_code == 201:
        return f"Call created successfully: {response.json()}"
    else:
        return f"Failed to create call: {response.text}"

# Handle rescue call requests
@call_rescue_agent.on_message(model=CallRescueRequest)
async def handle_call_rescue_request(ctx: Context, sender: str, msg: CallRescueRequest):
    # Step 1: Send the message to Hyperbolic's LLaMA API for summarization
    ctx.logger.info("Sending message to Hyperbolic LLaMA for summarization...")
    summary = call_llama_vision_for_summary(msg.message)

    ctx.logger.info(f"Received summary from LLaMA: {summary}")
    
    # Step 2: Send the summarized message to VAPI to create the phone call
    response = create_vapi_call(summary)

    # Log the result
    ctx.logger.info(response)

# On startup, log and print the agent's address
@call_rescue_agent.on_event("startup")
async def introduce(ctx: Context):
    ctx.logger.info(f"Call Rescue Agent is starting. Address: {ctx.address}")
    print(f"Call Rescue Agent Address: {ctx.address}")

if __name__ == "__main__":
    call_rescue_agent.run()
