import openai
from colorama import init, Fore, Style

init(autoreset=True)


def transcribe(audio_filepath, prompt: str) -> str:
    try:
        transcript = openai.Audio.transcribe(
            file=open(audio_filepath, "rb"),
            model="whisper-1",
            prompt=prompt,
        )
        return transcript["text"]
    except openai.error.OpenAIError as api_err:
        print(Style.BRIGHT + Fore.RED + "API Error:", api_err)
    except Exception as e:
        print(Style.BRIGHT + Fore.RED + "Error:", e)
    return ""


def remove_non_ascii(text: str) -> str:
    return ''.join(i for i in text if ord(i) < 128)


def transcribe_and_clean(mp3_filepath, prompt: str) -> str:
    transcription = transcribe(mp3_filepath, prompt)
    if transcription:
        cleaned_transcription = remove_non_ascii(transcription)
        return cleaned_transcription
    else:
        return "Transcription failed. Please try again."
