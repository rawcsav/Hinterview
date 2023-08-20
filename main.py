import asyncio
import threading
import tiktoken
import pyaudio
from pydub import AudioSegment
from pynput import keyboard
from openai_util import embed_documents, ask
from whisper_util import transcribe_and_clean
from colorama import init, Fore
from config import configure_settings
from gui_util import display_intro, display_footer, display_recording, display_transcribing, display_processing, \
    clear_screen, display_instructions

init(autoreset=True)

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
MP3_OUTPUT_FILENAME = "temp.mp3"
DEVICE_INDEX = 1  # Index for BlackHole 2ch

audio = pyaudio.PyAudio()
tokenizer = tiktoken.get_encoding("cl100k_base")

is_recording = False
frames = []
exit_program = False


def record_audio():
    global frames, exit_program

    display_recording()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True, input_device_index=DEVICE_INDEX,
                        frames_per_buffer=CHUNK)

    while is_recording:
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
    transcription = transcribe_and_clean(MP3_OUTPUT_FILENAME, "This is an excerpt from a job interview.")
    # Check if transcription was successful
    if transcription != "Transcription failed. Please try again.":
        display_processing()
        asyncio.run(ask(transcription, df))
    else:
        print(Fore.RED + transcription)  # Display the error message

    frames.clear()
    exit_program = True


def on_press(key):
    global is_recording
    if key == getattr(keyboard.Key, hotkey) and not is_recording:
        is_recording = True
        threading.Thread(target=record_audio).start()


def on_release(key):
    global is_recording
    if key == getattr(keyboard.Key, hotkey) and is_recording:
        is_recording = False


if __name__ == "__main__":
    clear_screen()  # Ensuring the console is clear at the start
    display_intro()
    folder_path, openai_api_key, hotkey, special_option, resume_title, job_desc_title = configure_settings()
    df = embed_documents(folder_path)
    display_instructions()
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    display_footer()
