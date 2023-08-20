import configparser
from colorama import Fore, Style
import openai
import os


def configure_settings():
    config = configparser.ConfigParser()

    # Check if the configuration file exists
    if os.path.exists('config.ini'):
        config.read('config.ini')
        folder_path = config.get('SETTINGS', 'folder_path', fallback=None)
        openai_api_key = config.get('SETTINGS', 'openai_api_key', fallback=None)
        hotkey = config.get('SETTINGS', 'hotkey', fallback=None)
        special_option = config.getboolean('SETTINGS', 'special_option', fallback=None)
        resume_title = config.get('SETTINGS', 'resume_title', fallback=None)
        job_desc_title = config.get('SETTINGS', 'job_desc_title', fallback=None)
    else:
        folder_path = None
        openai_api_key = None
        hotkey = None
        special_option = None
        resume_title = None
        job_desc_title = None

    # Ask user for folder path
    if not folder_path:
        folder_path = input(Fore.GREEN + "Please enter the path to the directory containing the .txt documents: ")
    else:
        print(Fore.LIGHTGREEN_EX + "Current directory path:" + Style.BRIGHT + f"{folder_path}")

    # Ask user for OpenAI API key
    if not openai_api_key:
        openai_api_key = input(Fore.GREEN + "Please enter your OpenAI API key: ")
    else:
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + f"Using the existing OpenAI API key.")

    # Ask user for hotkey
    if not hotkey:
        hotkey = input(Fore.GREEN + "Please specify the hotkey you'd like to use (e.g., 'alt_r'): ")
    else:
        print(Fore.LIGHTGREEN_EX + "Current hotkey:" + Style.BRIGHT + f"{hotkey}")

    # Ask user if they want to use the special interview option
    if special_option is None:
        response = input(Fore.GREEN + "Do you want to use the special interview option? (yes/no): ")
        special_option = True if response.lower() == 'yes' else False

    # If special option is enabled, ask for resume and job description titles
    if special_option:
        print(Fore.LIGHTGREEN_EX + "Special Interview Option is" + Style.BRIGHT + " enabled.")
        if not resume_title:
            resume_title = input(
                Fore.GREEN + "Please enter the title of your resume document (without .txt extension): ")
        else:
            print(Fore.LIGHTGREEN_EX + "Current resume title:" + Style.BRIGHT + f"{resume_title}")

        if not job_desc_title:
            job_desc_title = input(
                Fore.GREEN + "Please enter the title of the job description document (without .txt extension): ")
        else:
            print(Fore.LIGHTGREEN_EX + f"Current job description title:" + Style.BRIGHT + f"{job_desc_title}")
    else:
        print(Fore.LIGHTGREEN_EX + "Special Interview Option is" + Style.BRIGHT + " disabled.")

        # Save the configuration for future use
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    openai.api_key = openai_api_key

    # Storing all configurations in a dictionary
    global config_data
    config_data = {
        'folder_path': folder_path,
        'openai_api_key': openai_api_key,
        'hotkey': hotkey,
        'resume_title': resume_title,
        'job_desc_title': job_desc_title,
        'special_option': special_option
    }

    return folder_path, openai_api_key, hotkey, special_option, resume_title, job_desc_title


# Function to fetch configuration values
def get_config(key):
    return config_data.get(key, None)
