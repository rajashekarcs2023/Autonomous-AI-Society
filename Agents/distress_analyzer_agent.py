

# API Keys (replace these with actual keys)
DEEPGRAM_API_KEY = ""
GROQ_API_KEY = ""
HUME_API_KEY = ""


from uagents import Agent, Context, Model
import sys
import asyncio
import pyaudio
import wave
import requests

from hume import AsyncHumeClient
from hume.expression_measurement.stream import Config
from hume.expression_measurement.stream.socket_client import StreamConnectOptions
import time
from deepgram import DeepgramClient, SpeakOptions
from pygame import mixer
import time

# Define the distress analyzer agent
distress_analyzer_agent = Agent(
    name="distress_analyzer",
    port=8002,
    seed="distress_analyzer_secret_seed",
    endpoint=["http://127.0.0.1:8002/submit"],
)

class DistressAnalysisRequest(Model):
    duration: int

class DroneDispatchRequest(Model):
    target_city: str

@distress_analyzer_agent.on_event("startup")
async def introduce(ctx: Context):
    ctx.logger.info(f"Distress Analyzer Agent is starting. Address: {ctx.address}")

@distress_analyzer_agent.on_message(model=DistressAnalysisRequest)
async def handle_distress_analysis(ctx: Context, sender: str, msg: DistressAnalysisRequest):
    ctx.logger.info(f"Received distress analysis request for {msg.duration} seconds.")
    await process_distress_calls(ctx)

import os

# Path to the distress_details folder
DISTRESS_DETAILS_PATH = os.path.join(os.path.dirname(__file__), 'distress_details')

# Ensure the distress_details directory exists
os.makedirs(DISTRESS_DETAILS_PATH, exist_ok=True)

async def process_distress_calls(ctx):
    distress_audio_files = []
    distress_data = []

    # Record 5 audio messages and process each one
    for i in range(5):
        file_name = f"distress_recording_{i + 1}.wav"
        print(f"Recording {file_name}...")

        # Record the audio
        record_audio(file_name, 5)
        distress_audio_files.append(file_name)

        # Transcribe the audio
        transcription = await transcribe_audio(file_name)
        if not transcription:
            print(f"Error: Transcription for {file_name} failed.", file=sys.stderr)
            continue

        # Analyze distress for this audio
        prosody_result = await analyze_audio(file_name)
        distress_level = interpret_distress(prosody_result)
        if distress_level == "Error":
            print(f"Error: Distress analysis for {file_name} failed.", file=sys.stderr)
            continue

        # Store distress data (distress level, transcription, and file name)
        distress_data.append((distress_level, transcription, file_name))

        # Write distress call details to file
        distress_call_filename = os.path.join(DISTRESS_DETAILS_PATH, f'distress_call_{i + 1}.txt')
        with open(distress_call_filename, 'w') as f:
            f.write(f"Transcription for {file_name}: {transcription}\n")
            f.write(f"Distress Level for {file_name}: {distress_level}\n")

    # Find the audio file with the highest distress level
    if distress_data:
        highest_distress = max(distress_data, key=lambda x: x[0])
        highest_transcription = highest_distress[1]
        print(f"Highest Distress Level: {highest_distress[0]} from file {highest_distress[2]}")

        # Identify city, with fallback to Miami
        city = identify_city(highest_transcription)
        print(f"Identified City: {city}")

        # Generate and print the dramatic message
        dramatic_message = f"High priority distress call came from the city: {city}. We're in the middle of Hurricane Milton, and the wind is getting stronger. I'm here with my elderly parents, and we've lost power. My dad has a heart condition, and he's starting to feel unwell. We're running low on food and water too. The roads are completely flooded, and I can hear trees cracking outside. I don't think we can leave on our own. Please send medical assistance and evacuation teams as soon as you can."
        print(dramatic_message)

        # **Step 1: Send the dramatic message to Groq to summarize it**
        summarized_message = summarize_message_with_groq(dramatic_message)
        print(f"Summarized Message: {summarized_message}")

        # Write the final summary and highest distress details to a file
        final_summary_filename = os.path.join(DISTRESS_DETAILS_PATH, 'final_summary.txt')
        with open(final_summary_filename, 'w') as f:
            f.write(f"Highest Distress Level: {highest_distress[0]} from file {highest_distress[2]}\n")
            f.write(f"Identified City: {city}\n")
            f.write(f"Summarized Message: {summarized_message}\n")

        # Convert the summarized message to audio and play it
        filename = "test_output.mp3"
        success = await generate_audio(summarized_message, filename)
        if success:
            print("Playing the generated audio...")
            play_audio(filename)
        else:
            print("Failed to generate dramatic message audio.")

        # **Step 4: Automatically call the drone dispatch after reading out the message**
        await send_city_to_bob(ctx, city)
    else:
        print("No valid distress recordings found.")



# Function to send the identified city to Bob's agent
async def send_city_to_bob(ctx, city):
    bob_address = "agent1qgwfm2zw66prpxu6krzafy2l7e3fjzsvm4p4p7ryngssnhwgs2d7vt4tl6f"  # Use Bob's actual address here
    ctx.logger.info(f"Sending city '{city}' to Bob's agent at {bob_address}")
    
    await ctx.send(bob_address, DroneDispatchRequest(target_city=city))

    ctx.logger.info(f"High priority distress call from {city} sent to Bob's agent.")
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
# Function to record audio and save it as a .wav file
def record_audio(filename, duration=5):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = duration

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print(f"* Recording for {RECORD_SECONDS} seconds...")

    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* Recording finished")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# Function to transcribe audio using Deepgram
async def transcribe_audio(file_path):
    try:
        dg_client = DeepgramClient(DEEPGRAM_API_KEY)

        with open(file_path, "rb") as audio_file:
            buffer_data = audio_file.read()

        options = {
            "model": "nova-2",
            "smart_format": True,
            "utterances": True,
            "punctuate": True,
            "diarize": True,
        }

        print("Sending request to Deepgram for transcription...")

        response = dg_client.listen.rest.v("1").transcribe_file(
            {"buffer": buffer_data}, options
        )
        
        transcription = response['results']['channels'][0]['alternatives'][0]['transcript']
        return transcription

    except Exception as e:
        print(f"Transcription error: {e}")
        return ""

# Function to analyze audio and calculate distress score using Hume
async def analyze_audio(file_path):
    client = AsyncHumeClient(api_key=HUME_API_KEY)
    
    model_config = Config(prosody={})
    stream_options = StreamConnectOptions(config=model_config)
    
    async with client.expression_measurement.stream.connect(options=stream_options) as socket:
        result = await socket.send_file(file_path)
        return result

# Function to interpret distress levels from prosody results
def interpret_distress(prosody_result):
    distress_emotions = ['Stress', 'Anxiety', 'Fear', 'Sadness']
    
    if not hasattr(prosody_result, 'prosody') or not hasattr(prosody_result.prosody, 'predictions'):
        return "Error", "Invalid response structure from Hume API."
    
    first_prediction = prosody_result.prosody.predictions[0]
    
    emotion_scores = first_prediction.emotions
    distress_level = sum(emotion.score for emotion in emotion_scores if emotion.name in distress_emotions)
    
    return distress_level

def summarize_message_with_groq(dramatic_message):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant that summarizes distress messages in a concise format."
            },
            {
                "role": "user",
                "content": f"Summarize this distress message: '{dramatic_message}'"
            }
        ],
        "max_tokens": 100  # Adjust token limit as necessary
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        summary = data['choices'][0]['message']['content'].strip()

        return summary
    except Exception as e:
        print(f"Error summarizing message: {e}")
        return dramatic_message  # Fallback to the full message if summarization fails


# Function to identify the city mentioned in the transcription
def identify_city(transcription):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant that extracts only the city name from transcripts."
            },
            {
                "role": "user",
                "content": f"Extract only the city name in one word from this transcript: '{transcription}'"
            }
        ],
        "max_tokens": 10  # Limit to a short response to just the city name
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        city = data['choices'][0]['message']['content'].strip()

        # Fallback to "Miami" if no city is detected
        if not city:
            return "Miami"
        
        return city
    except Exception as e:
        return "Miami"  # Return "Miami" in case of any failure


if __name__ == "__main__":
    distress_analyzer_agent.run()
