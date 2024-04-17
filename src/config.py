import configparser
import json
import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
import openai
from colorama import init

init(autoreset=True)

load_dotenv()

config_data: Dict[str, Any] = {}

def open_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()

    if Path("config.ini").exists():
        config.read("config.ini")
    else:
        config["SETTINGS"] = {
            "folder_path": "",
            "openai_api_key": "",
            "hotkey": "alt_l",
            "gpt_model": "gpt-4-turbo",
            "system_prompt": "You are a knowledgeable job interview assistant that uses information from provided textual excerpts to provide impressive, but concise answers to interview questions.",
            "temperature": "1.0",
            "top_p": "1.0",
            "max_tokens": "1000",
        }
        config["FILES"] = {}  # Add an empty [FILES] section
        with open("config.ini", "w") as configfile:
            config.write(configfile)

    if not config.has_section("FILES"):
        config.add_section("FILES")

    return config
def get_config(key: str) -> Any:
    return config_data.get(key)

def get_user_input(prompt, fallback=None, strip_quotes=True):
    """Get user input with an optional fallback and option to strip surrounding quotes."""
    response = input(prompt)
    if strip_quotes:
        response = response.strip('"')
    return response if response else fallback

def configure_folder_path(config):
    """Configure the folder path setting."""
    folder_path = config.get('SETTINGS', 'folder_path', fallback=None)
    if not folder_path:
        folder_path = get_user_input("Enter directory path for .txt or .pdf documents: ")
        config['SETTINGS']['folder_path'] = folder_path
    return folder_path

def configure_api_key(config):
    """Configure the OpenAI API key setting."""
    openai_api_key = config.get('SETTINGS', 'openai_api_key', fallback=None)
    if not openai_api_key:
        openai_api_key = get_user_input("Enter your OpenAI API key: ")
        config['SETTINGS']['openai_api_key'] = openai_api_key
    return openai_api_key

def configure_hotkey(config):
    """Configure the hotkey setting."""
    hotkey = config.get('SETTINGS', 'hotkey', fallback='alt_r')
    return hotkey


def configure_file_types(folder_path):
    config = configparser.ConfigParser()
    config.read("config.ini")

    if not config.has_section("FILES"):
        config.add_section("FILES")

    # Remove file types for files that are no longer present
    existing_files = set(os.path.basename(file) for file in os.listdir(folder_path))
    config_files = set(config.options("FILES"))
    removed_files = config_files - existing_files

    for filename in removed_files:
        config.remove_option("FILES", filename)

    # Prompt for file types for new files
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt") or filename.endswith(".pdf"):
            if not config.has_option("FILES", filename):
                file_type = get_user_input(f"Indicate the type of file '{filename}' (resume/job_description/company_description/other/none): ", "none", False)
                if file_type.lower() != "none":
                    config.set("FILES", filename, file_type)

    with open("config.ini", "w") as configfile:
        config.write(configfile)

def save_config(config):
    """Save the updated configuration to the file."""
    with open("config.ini", "w") as configfile:
        config.write(configfile)

def configure_user_settings():
    config = open_config()
    folder_path = configure_folder_path(config)
    openai_api_key = configure_api_key(config)
    hotkey = configure_hotkey(config)

    save_config(config)

    return folder_path, openai_api_key, hotkey


def get_file_type(filename):
    config = configparser.ConfigParser()
    config_file = Path("config.ini")

    if config_file.exists():
        config.read(config_file)
    else:
        return "other"

    if not config.has_section("FILES"):
        return "other"

    if config.has_option("FILES", filename):
        file_type = config.get("FILES", filename)
        if file_type.lower() != "none":
            return file_type
    return "other"

def configure_gpt_settings() -> tuple:
    config = open_config()

    gpt_model = config.get("SETTINGS", "gpt_model") or os.getenv("GPT_MODEL", "gpt-4-turbo")
    system_prompt = (
        config.get("SETTINGS", "system_prompt")
        or os.getenv(
            "SYSTEM_PROMPT",
            "You are a knowledgeable job interview assistant that uses information from provided textual excerpts to provide impressive, but concise answers to interview questions.",
        )
    )
    temperature = config.getfloat("SETTINGS", "temperature") or float(os.getenv("TEMPERATURE", "1.0"))
    top_p = config.getfloat("SETTINGS", "top_p") or float(os.getenv("TOP_P", "1.0"))
    max_tokens = config.getint("SETTINGS", "max_tokens") or int(os.getenv("MAX_TOKENS", "1000"))

    config["SETTINGS"]["gpt_model"] = gpt_model
    config["SETTINGS"]["system_prompt"] = system_prompt
    config["SETTINGS"]["temperature"] = str(temperature)
    config["SETTINGS"]["top_p"] = str(top_p)
    config["SETTINGS"]["max_tokens"] = str(max_tokens)

    config_data.update(
        {
            "gpt_model": gpt_model,
            "system_prompt": system_prompt,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
        }
    )

    return gpt_model, system_prompt, temperature, top_p, max_tokens


def configure_settings(**kwargs: Any) -> tuple:
    config = open_config()
    user_settings = configure_user_settings()
    gpt_settings = configure_gpt_settings()

    if kwargs:
        for key, value in kwargs.items():
            config["SETTINGS"][key] = str(value)
            config_data[key] = value

    with open("config.ini", "w") as configfile:
        config.write(configfile)

    config_data.update(
        dict(
            zip(
                [
                    "folder_path",
                    "openai_client",
                    "hotkey",
                    "gpt_model",
                    "system_prompt",
                    "temperature",
                    "top_p",
                    "max_tokens",
                ],
                user_settings + gpt_settings,
            )
        )
    )

    return user_settings + gpt_settings