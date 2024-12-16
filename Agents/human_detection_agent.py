
import os
import base64
import requests
from io import BytesIO
from PIL import Image
from uagents import Agent, Context, Model
import random
from deepgram import DeepgramClient, SpeakOptions
from pygame import mixer
import asyncio
import time

# Initialize the human detection agent
human_detection_agent = Agent(
    name="human_detection_agent",
    port=8005,
    seed="human_detection_secret_seed",
    endpoint=["http://127.0.0.1:8005/submit"],
)

# Deepgram API Key
DEEPGRAM_API_KEY = ""

class HumanDetectionRequest(Model):
    folder_path: str  # Path to the folder containing images

class CallRescueRequest(Model):
    message: str  # The full message containing rescue details

# Encode image to base64
def encode_image(img):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    encoded_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return encoded_string

# Call Hyperbolic LLaMA Vision API
def call_llama_vision(image, prompt="Are there humans in this image? and if they are there, give a very small concise description of the image in 1-2 lines which would help the rescue team minimize loss of life and save those humans or any animal life. But if the humans in the image seem to be normal and if the situation is a normal one or if the humans are enjoying, just say that they are fine and no rescue efforts needed."):
    """
    Call Hyperbolic LLaMA Vision API with an image and optional prompt
    """
    api = "https://api.hyperbolic.xyz/v1/chat/completions"
    api_key = ""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    base64_img = encode_image(image)
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"},
                    },
                ],
            }
        ],
        "model": "Qwen/Qwen2-VL-72B-Instruct",
        "max_tokens": 2048,  # Updated to match new documentation
        "temperature": 0.7,
        "top_p": 0.9,
    }

    response = requests.post(api, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to call LLaMA Vision API"}

# Generate random coordinates in Florida
def get_random_coordinates():
    latitude = round(random.uniform(24.396308, 31.000968), 6)
    longitude = round(random.uniform(-87.634938, -80.031362), 6)
    return {"latitude": latitude, "longitude": longitude}

# Function to process all images in the specified folder
def process_images_in_folder(folder_path):
    # Create the descriptions folder if it doesn't exist
    descriptions_folder = os.path.join(os.getcwd(), "descriptions")
    if not os.path.exists(descriptions_folder):
        os.makedirs(descriptions_folder)

    results = []

    # Iterate over all .jpg images in the folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".jpg"):
            image_path = os.path.join(folder_path, filename)
            image = Image.open(image_path)

            # Call LLaMA Vision API to detect humans
            llama_result = call_llama_vision(image)
            if "error" in llama_result:
                print(f"Error processing image {filename}: {llama_result['error']}")
                continue

            # Extract the description from the response
            description = llama_result.get("choices", [])[0].get("message", {}).get("content", "")
            if not description:
                print(f"No description received for image {filename}.")
                continue

            # Get random coordinates
            coordinates = get_random_coordinates()

            # Store the result
            results.append({
                "filename": filename,
                "description": description.strip(),
                "coordinates": coordinates,
            })
            print(f"Processed image {filename}.")

    # Save results to the descriptions folder
    output_file_path = os.path.join(descriptions_folder, "processed_results.txt")
    with open(output_file_path, "w") as f:
        for result in results:
            f.write(f"File: {result['filename']}\n")
            f.write(f"Description: {result['description']}\n")
            f.write(f"Coordinates: {result['coordinates']}\n\n")

    print(f"Results saved to: {output_file_path}")

# Function to generate the audio message using Deepgram
async def generate_audio(text, filename):
    dg_client = DeepgramClient(DEEPGRAM_API_KEY)
    options = SpeakOptions(model="aura-asteria-en")
    speak_options = {"text": text}

    try:
        response = dg_client.speak.v("1").save(filename, speak_options, options)
        print(f"Audio saved to {filename}")
        return True
    except Exception as e:
        print(f"Error generating audio: {e}")
        return False

def play_audio(filename):
    mixer.init()
    sound = mixer.Sound(filename)
    sound.play()
    while mixer.get_busy():
        time.sleep(0.1)
    mixer.quit()

# Function to play the audio message after human detection
async def play_audio_message():
    message = "Live streaming images from the drone have detected some humans. Please review the drone results immediately and take action."
    filename = "drone_audio_message.mp3"
    await asyncio.sleep(8)
    success = await generate_audio(message, filename)
    if success:
        print("Playing the generated audio...")
        play_audio(filename)
    else:
        print("Failed to generate audio.")

@human_detection_agent.on_event("startup")
async def introduce(ctx: Context):
    ctx.logger.info(f"Human Detection Agent is starting. Address: {ctx.address}")
    print(f"Human Detection Agent Address: {ctx.address}")

@human_detection_agent.on_message(model=HumanDetectionRequest)
async def handle_human_detection_request(ctx: Context, sender: str, msg: HumanDetectionRequest):
    folder_path = msg.folder_path
    if not os.path.exists(folder_path):
        ctx.logger.error("Folder not found.")
        return

    # Process images in the specified folder
    process_images_in_folder(folder_path)

    ctx.logger.info(f"Human detection processing completed for folder: {folder_path}")

    # Play the audio message using Deepgram
    await play_audio_message()

    # Trigger the call_rescue_agent after playing the audio message
    rescue_message = """
    There is a child trapped on the roof of a house, surrounded by floodwaters. The rescue team needs to reach coordinates (latitude: 25.50798, longitude: -84.19412).
    The water level is rising, and the child is in immediate danger.
    """
    CALL_RESCUE_AGENT_ADDRESS = "agent1qv306rfgyvyhpyfdwavl625lh4383kchky39rkqdcz0s7s7t93yjglrjxrr"
    await ctx.send(CALL_RESCUE_AGENT_ADDRESS, CallRescueRequest(message=rescue_message))
    ctx.logger.info("Triggered the call_rescue_agent after human detection processing.")

if __name__ == "__main__":
    human_detection_agent.run()
