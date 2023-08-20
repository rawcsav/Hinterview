# Hinterview - AI Interview Assistant

## Features

- Audio Transcription with Whisper ASR: Quickly transcribe interview audio segments in real-time using OpenAI's powerful Whisper ASR system.
- Interactive CLI: An intuitive command-line interface designed with colorama for colored feedback, providing visual cues for recording, transcribing, and AI response statuses.
- Real-time Insights with OpenAI: Transcribed segments are analyzed by OpenAI to provide insights and responses. Embeds documents for a more contextual understanding of interview questions.
- Configurable Settings: A flexible configuration system utilizing configparser allows users to adjust settings for directory paths, OpenAI API keys, and preferred hotkeys. The special interview option (`special_option`) facilitates the use of resume and job description documents for enhanced insights.

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

Create a config.ini in the root directory of the project. Add the following:

```ini
[SETTINGS]
folder_path = YOUR_FOLDER_PATH
openai_api_key = YOUR_OPENAI_API_KEY
hotkey = YOUR_PREFERRED_HOTKEY
special_option = True or False
resume_path = YOUR_RESUME_PATH (if special_option = True)
job_description_path = YOUR_JOB_DESCRIPTION_PATH (if special_option = True)
```

Run the Application:

```bash
python main.py
```

## Usage

- Start the Application: Run `python main.py`.
- Follow On-screen Instructions: The CLI will guide you on how to record, transcribe, and obtain insights for your interviews.
- Hotkey Driven: The application uses a hotkey (configurable) for starting and stopping audio recording. Once recording is stopped, the audio segment is transcribed and analyzed.
- Adjust Settings as Needed: The config.py script facilitates the configuration of various settings including the OpenAI API key, folder paths, hotkeys, and more. If the config.ini file is missing or incomplete, the user is prompted to provide necessary details.
- Special Interview Option: When `special_option` is set to True in the config.ini file, you can specify the paths for your resume and the job description by setting `resume_path` and `job_description_path`. The application will include at least one excerpt from each of these documents when providing AI-generated responses to interview questions, ensuring a more personalized and tailored response.

## MacOS Configuration

This project was developed and tested on MacOS. For capturing audio, it's designed to use BlackHole as a virtual microphone. Audio is captured at a rate of 44100Hz in stereo format. Audio segments are temporarily saved as MP3 files for transcription. You can set up BlackHole by creating a multi-output device in the Audio MIDI settings.

## Acknowledgements

- [OpenAI Whisper ASR System](https://openai.com/research/whisper-asr): Used for real-time audio transcription.
- [OpenAI API](https://openai.com/api/): Enables embedding of documents and querying the model for insights.
- [Colorama](https://pypi.org/project/colorama/): Provides the colorful CLI experience.
- [BlackHole](https://existential.audio/blackhole/): Used as a virtual microphone for capturing audio on MacOS.
