import pygame
import os
import math
import sys
import asyncio
from pygame import mixer
from deepgram import DeepgramClient, SpeakOptions

DEEPGRAM_API_KEY = "d6474c2ed5a5c94cd35f1e0616e2998a7c9d6d01"

def load_image(name):
    fullname = os.path.join(os.getcwd(), name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print(f'Cannot load image: {name}')
        raise SystemExit(message)
    return image, image.get_rect()

def resize_image(image, max_width, max_height):
    width, height = image.get_size()
    aspect_ratio = width / height
    if width > max_width:
        width = max_width
        height = int(width / aspect_ratio)
    if height > max_height:
        height = max_height
        width = int(height * aspect_ratio)
    return pygame.transform.smoothscale(image, (width, height))

def lat_lon_to_pixel(lat, lon, min_lat, max_lat, min_lon, max_lon, width, height):
    x = (lon - min_lon) / (max_lon - min_lon) * width
    y = height - ((lat - min_lat) / (max_lat - min_lat) * height)
    return int(x), int(y)

def load_drone_image(name, size):
    fullname = os.path.join(os.getcwd(), name)
    try:
        image = pygame.image.load(fullname)
        scale_factor = 1
        new_size = (int(size[0] * scale_factor), int(size[1] * scale_factor))
        return pygame.transform.scale(image, new_size)
    except pygame.error as message:
        print(f'Cannot load image: {name}')
        raise SystemExit(message)

def rotate_drone(image, angle):
    return pygame.transform.rotate(image, math.degrees(angle))

async def generate_audio(text, filename):
    dg_client = DeepgramClient(DEEPGRAM_API_KEY)
    options = SpeakOptions(model="aura-asteria-en")
    speak_options = {"text": text}
    
    try:
        response = dg_client.speak.v("1").save(filename, speak_options, options)
        print(f"Audio saved to {filename}")
    except Exception as e:
        print(f"Error generating audio: {e}")

async def prepare_audio_files(target_city_name):
    await generate_audio(f"Dispatch started for {target_city_name}", "start.mp3")
    await generate_audio(f"Dispatch has reached {target_city_name}. Mission completed", "complete.mp3")

def drone_response_simulation(target_city_name):
    # Run the async function to generate audio files
    asyncio.run(prepare_audio_files(target_city_name))

    pygame.init()
    mixer.init()

    # Load sound effects
    start_sound = mixer.Sound('start.mp3')
    drone_sound = mixer.Sound('drone.wav')
    complete_sound = mixer.Sound('complete.mp3')

    max_width, max_height = 1000, 800
    screen = pygame.display.set_mode((max_width, max_height))
    pygame.display.set_caption("Florida Drone Response Simulation")

    try:
        original_map, _ = load_image('florida.png')
        florida_map = resize_image(original_map, max_width, max_height)
        width, height = florida_map.get_size()
        screen = pygame.display.set_mode((width, height))
    except pygame.error as e:
        return f"Simulation failed: Error loading image: {str(e)}"

    clock = pygame.time.Clock()

    min_lat, max_lat = 24.396308, 31.000888
    min_lon, max_lon = -87.634643, -79.974307

    RED = (255, 0, 0)
    BLACK = (0, 0, 0)

    font = pygame.font.Font(None, 24)

    drone_size = (30, 30)
    drone_image = load_drone_image('drone.jpg', drone_size)

    drone_lat, drone_lon = (max_lat + min_lat) / 2, (max_lon + min_lon) / 2
    drone_speed = 0.005
    drone_angle = 0

    cities = [
        {"name": "Miami", "lat": 25.6614, "lon": -80.7718},
        {"name": "Orlando", "lat": 28.0380, "lon": -81.5592},
        {"name": "Tampa", "lat": 27.4406, "lon": -82.4572},
        {"name": "Jacksonville", "lat": 29.6682, "lon": -81.6557},
        {"name": "Tallahassee", "lat": 29.7780, "lon": -83.7807},
        {"name": "Pensacola", "lat": 29.8810, "lon": -86.2169}
    ]

    target_city = next((c for c in cities if c["name"].lower() == target_city_name.lower()), None)
    if not target_city:
        pygame.quit()
        return f"City '{target_city_name}' not found. Simulation aborted."

    mission_active = True
    print(f"Distress signal received from {target_city['name']}!")

    # Play start sound
    start_sound.play()
    pygame.time.wait(int(start_sound.get_length() * 1000))  # Wait for the sound to finish

    # Start looping drone sound
    drone_channel = drone_sound.play(-1)  # -1 means loop indefinitely

    running = True
    frame_count = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(florida_map, (0, 0))

        for city in cities:
            x, y = lat_lon_to_pixel(city["lat"], city["lon"], min_lat, max_lat, min_lon, max_lon, width, height)
            pygame.draw.circle(screen, RED, (x, y), 5)
            
            if city["name"] == target_city["name"]:
                # Blink the target city name and add "High distress" message
                if frame_count % 60 < 30:  # Blink every half second
                    text_color = RED
                    city_text = f"{city['name']} [High distress]"
                else:
                    text_color = BLACK
                    city_text = city["name"]
            else:
                text_color = BLACK
                city_text = city["name"]
            
            text = font.render(city_text, True, text_color)
            text_rect = text.get_rect(center=(x, y - 15))
            screen.blit(text, text_rect)

        if mission_active:
            drone_angle = math.atan2(target_city["lat"] - drone_lat, target_city["lon"] - drone_lon)
            
            drone_lat += drone_speed * math.sin(drone_angle)
            drone_lon += drone_speed * math.cos(drone_angle)

            distance = math.sqrt((target_city["lat"] - drone_lat)**2 + (target_city["lon"] - drone_lon)**2)
            if distance < 0.05:
                mission_active = False
                # Stop drone sound
                drone_channel.stop()
                # Play complete sound
                complete_sound.play()
                pygame.time.wait(int(complete_sound.get_length() * 1000))  # Wait for the sound to finish
                running = False

        drone_x, drone_y = lat_lon_to_pixel(drone_lat, drone_lon, min_lat, max_lat, min_lon, max_lon, width, height)
        rotated_drone = rotate_drone(drone_image, -drone_angle)
        drone_rect = rotated_drone.get_rect(center=(drone_x, drone_y))
        screen.blit(rotated_drone, drone_rect)

        instructions = font.render(f"Mission active: Heading to {target_city['name']}", True, BLACK)
        screen.blit(instructions, (10, 10))

        pygame.display.flip()
        clock.tick(60)
        frame_count += 1

    pygame.quit()
    return f"Mission complete! Drone has reached {target_city['name']}."

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python drone_simulation.py <city_name>")
        sys.exit(1)
    
    target_city = sys.argv[1]
    result = drone_response_simulation(target_city)
    print(result)
    sys.stdout.flush()