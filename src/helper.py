import threading
import asyncio
from config import get_config, configure_user_settings
from gui_util import display_recording, display_transcribing, display_processing, \
    clear_screen, primary_gui
import pyaudio
from pydub import AudioSegment
from pynput import keyboard
from colorama import init, Fore
from openai_util import transcribe_and_clean, ask

init(autoreset=True)

df = primary_gui()

HOTKEY = get_config("hotkey")
FOLDER_PATH = get_config("folder_path")

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
MP3_OUTPUT_FILENAME = "temp.mp3"
DEVICE_INDEX = 1  # Index for BlackHole 2ch
audio = pyaudio.PyAudio()

recording_event = threading.Event()
interruption_event = threading.Event()

def record_audio():

    frames = []
    display_recording()

    try:
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True, input_device_index=DEVICE_INDEX,
                            frames_per_buffer=CHUNK)

        while recording_event.is_set():
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()

        audio_segment = AudioSegment(
            data=b''.join(frames),
            sample_width=audio.get_sample_size(FORMAT),
            frame_rate=RATE,
            channels=CHANNELS
        )
        audio_segment.export(MP3_OUTPUT_FILENAME, format="mp3", bitrate="64k")

        display_transcribing()
        transcription_result = transcribe_and_clean(MP3_OUTPUT_FILENAME)

        if transcription_result != "Transcription failed. Please try again.":
            if not interruption_event.is_set():  # Only process if not interrupted
                display_processing()
                asyncio.run(ask(transcription_result, df, interruption_event))
        else:
            print(Fore.RED + transcription_result)
    finally:  # Display the error message
        frames.clear()

def on_press(key):
    if key == getattr(keyboard.Key, HOTKEY) and not recording_event.is_set():
        clear_screen()
        recording_event.set()
        threading.Thread(target=record_audio).start()
    interruption_event.set()

def on_release(key):
    if key == getattr(keyboard.Key, HOTKEY) and recording_event.is_set():
        recording_event.clear()
        interruption_event.clear()