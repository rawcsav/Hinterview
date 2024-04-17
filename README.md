# Hinterview - AI Interview Assistant

## Features

- Audio Transcription with Whisper ASR: Quickly transcribe interview audio segments in real-time using OpenAI's powerful Whisper ASR system.
- Interactive CLI: An intuitive command-line interface designed with colorama for colored feedback, providing visual cues for recording, transcribing, and AI response statuses.
- Real-time Insights with OpenAI: Transcribed segments are analyzed by OpenAI to provide insights and responses. Embeds documents for a more contextual understanding of interview questions.
- Configurable Settings: A flexible configuration system utilizing configparser allows users to adjust settings for directory paths, OpenAI API keys, and preferred hotkeys. 

## Prerequisites

- Python 3.8 or higher.
- OpenAI account to obtain the API key.
- MacOS with BlackHole set up for audio routing, specifically using the pyaudio library for audio input with a device index set for BlackHole 2ch.

## Installation

Clone the Repository:

```bash
git clone https://github.com/rawcsav/Hinterview.git
cd Hinterview
```

Install Dependencies:

```bash
pip install -r requirements.txt
```

Set Up Configuration:

Create a config.ini in the root directory of the project. Add/configure the following:

```ini
[SETTINGS]
folder_path = /path/to/your/folder
openai_api_key = your_openai_api_key
hotkey = your_preferred_hotkey
gpt_model = gpt-4-turbo
system_prompt = You are a knowledgeable job interview assistant that uses information from provided textual excerpts to provide impressive, but concise answers to interview questions.
temperature = 1.0
top_p= 1.0
max_tokens = 1000
```

Run the Application:

```bash
python src/main.py
```

## Usage

- Start the Application: Run `python main.py`.
- Follow On-screen Instructions: The CLI will guide you on how to record, transcribe, and obtain insights for your interviews.
- Hotkey Driven: The application uses a hotkey (configurable) for starting and stopping audio recording. Once recording is stopped, the audio segment is transcribed and analyzed.
- Adjust Settings as Needed: The config.py script facilitates the configuration of various settings including the OpenAI API key, folder paths, hotkeys, and more. If the config.ini file is missing or incomplete, the user is prompted to provide necessary details.


## MacOS Configuration

This project was developed and tested on MacOS. For capturing audio, it's designed to use BlackHole as a virtual microphone. Audio is captured at a rate of 44100Hz in stereo format. Audio segments are temporarily saved as MP3 files for transcription. 
`Important:` You need to set up BlackHole by creating a multi-output device in the Audio MIDI settings. Otherwise you will not be able to hear and capture the audio simultaneously.

## Acknowledgements

- [OpenAI Whisper ASR System](https://openai.com/research/whisper-asr): Used for real-time audio transcription.
- [OpenAI API](https://openai.com/api/): Enables embedding of documents and querying the model for insights.
- [Colorama](https://pypi.org/project/colorama/): Provides the colorful CLI experience.
- [BlackHole](https://existential.audio/blackhole/): Used as a virtual microphone for capturing audio on MacOS.
