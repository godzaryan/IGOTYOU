import sys
import numpy as np
import pygame
import pyaudio
from math import cos, sin, radians
from pygame.locals import *
from PIL import Image
from ctypes import cast, POINTER
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)  # Enable transparency
pygame.display.set_caption("AI Voice Assistant Visualizer")

# Colors and configurations
CIRCLE_COLOR = (0, 200, 255)
FPS = 60

# Audio setup (Desktop audio capture using pycaw)
p = pyaudio.PyAudio()

# Set up the audio stream for capturing system audio
device_index = None
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        device_index = i
        break

if device_index is None:
    print("No input device found.")
    sys.exit()

stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=1024)

# Load GIF using Pillow and extract frames
gif_path = 'your_gif.gif'  # Replace with your GIF file
gif_image = Image.open(gif_path)

# Extract GIF frames into a list
frames = []
for frame in range(gif_image.n_frames):
    gif_image.seek(frame)
    frame_image = gif_image.convert('RGBA')
    frame_surface = pygame.image.fromstring(frame_image.tobytes(), frame_image.size, 'RGBA')
    frames.append(frame_surface)

# GIF animation properties
frame_count = len(frames)
frame_delay = 1  # Milliseconds between frames, adjust as needed
current_frame = 0
last_update_time = pygame.time.get_ticks()

def get_desktop_audio_data():
    """Capture desktop audio data."""
    data = np.frombuffer(stream.read(1024, exception_on_overflow=False), dtype=np.int16)
    fft_data = np.abs(np.fft.rfft(data))[:50]  # Frequency spectrum
    return fft_data

def draw_circular_visualizer(audio_data, center, base_radius, max_radius):
    """Draw the circular visualizer."""
    num_bars = len(audio_data)
    angle_step = 360 / num_bars
    max_value = max(audio_data) if max(audio_data) > 0 else 1

    # Adjust sensitivity by modifying the scaling factor
    sensitivity_factor = 5
    scaled_audio_data = np.array(audio_data) / sensitivity_factor

    for i, value in enumerate(scaled_audio_data):
        angle = i * angle_step
        normalized_value = (value / max_value) * (max_radius - base_radius)

        # Calculate bar endpoints
        x1 = center[0] + base_radius * cos(radians(angle))
        y1 = center[1] + base_radius * sin(radians(angle))
        x2 = center[0] + (base_radius + normalized_value) * cos(radians(angle))
        y2 = center[1] + (base_radius + normalized_value) * sin(radians(angle))

        # Draw bar
        pygame.draw.line(screen, CIRCLE_COLOR, (x1, y1), (x2, y2), 2)

def main():
    global current_frame, last_update_time

    clock = pygame.time.Clock()
    running = True
    center = (WIDTH // 2, HEIGHT // 2)
    base_radius = 100
    max_radius = 200

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        # Clear screen with transparent background
        screen.fill((0, 0, 0, 0))  # Transparent background

        # Get desktop audio data and draw visualizer
        audio_data = get_desktop_audio_data()
        draw_circular_visualizer(audio_data, center, base_radius, max_radius)

        # Loop the GIF at the center
        # Check if it's time to update the GIF frame
        current_time = pygame.time.get_ticks()
        if current_time - last_update_time > frame_delay:
            last_update_time = current_time
            current_frame = (current_frame + 1) % frame_count  # Loop through frames

        # Resize the GIF to fit inside the visualizer
        gif_width, gif_height = frames[current_frame].get_size()
        max_gif_size = max_radius - base_radius  # Leave some margin around the circle
        scale_factor = min(max_gif_size / gif_width, max_gif_size / gif_height)

        # Resize the GIF frame
        resized_gif = pygame.transform.scale(frames[current_frame],
                                             (int(gif_width * scale_factor), int(gif_height * scale_factor)))

        # Draw the resized GIF at the center of the visualizer
        gif_rect = resized_gif.get_rect(center=center)
        screen.blit(resized_gif, gif_rect)

        # Update display
        pygame.display.flip()
        clock.tick(FPS)

    # Cleanup
    stream.stop_stream()
    stream.close()
    p.terminate()
    pygame.quit()

if __name__ == "__main__":
    main()
