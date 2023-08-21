import configparser
from colorama import Fore, Style, init
import os

init(autoreset=True)

config_data = {}


def configure_settings():
    config = configparser.ConfigParser()

    # Check if the configuration file exists
    if os.path.exists('config.ini'):
        config.read('config.ini')
    else:
        # Set default values for the configuration file
        config['SETTINGS'] = {
            'folder_path': '',
            'openai_api_key': '',
            'hotkey': 'alt_r',
            'special_option': 'True',
            'gpt_model': 'gpt-4',
            'system_prompt': 'You are a knowledgeable job interview assistant that uses information from provided textual excerpts to provide impressive, but concise answers to interview questions.',
            'temperature': '0.5',
            'max_tokens': '1000',
            'resume_title': '',
            'job_desc_title': ''
        }

    # Initialize the values for settings
    folder_path = config.get('SETTINGS', 'folder_path')
    openai_api_key = config.get('SETTINGS', 'openai_api_key')
    hotkey = config.get('SETTINGS', 'hotkey')
    special_option = config.getboolean('SETTINGS', 'special_option')
    gpt_model = config.get('SETTINGS', 'gpt_model')
    system_prompt = config.get('SETTINGS', 'system_prompt')
    temperature = config.getfloat('SETTINGS', 'temperature')
    max_tokens = config.getint('SETTINGS', 'max_tokens')
    resume_title = config.get('SETTINGS', 'resume_title')
    job_desc_title = config.get('SETTINGS', 'job_desc_title')

    # Ask user for folder path
    if not folder_path:
        folder_path = input(Fore.GREEN + "Please enter the path to the directory containing the .txt documents: ")
    else:
        print("Current directory path:"  + Fore.LIGHTGREEN_EX + Style.BRIGHT + f"{folder_path}")

    # Ask user for OpenAI API key
    if not openai_api_key:
        openai_api_key = input(Fore.GREEN + "Please enter your OpenAI API key: ")
    else:
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + f"Using existing OpenAI API key.")

    # Ask user if they want to use the special interview option
    if special_option is False:
        response = input(Fore.GREEN + "Do you want to use the special interview option? (y/n): ")
        special_option = True if response.lower() == 'y' else False

    # If special option is enabled, ask for resume and job description titles
    if special_option:
        if not resume_title:
            resume_title = input(Fore.GREEN + "Please enter the title for the resume document (without the .txt): ")
        else:
            print("Current resume title: "  + Fore.LIGHTGREEN_EX + Style.BRIGHT + f"{resume_title}")

        if not job_desc_title:
            job_desc_title = input(Fore.GREEN + "Please enter the title for the job description document (without the .txt): "  + "\n")
        else:
            print("Current job description title: "  + Fore.LIGHTGREEN_EX + Style.BRIGHT + f"{job_desc_title}" + "\n")

    # Save the new values to the configuration file
    config['SETTINGS']['folder_path'] = folder_path
    config['SETTINGS']['openai_api_key'] = openai_api_key
    config['SETTINGS']['hotkey'] = hotkey
    config['SETTINGS']['special_option'] = str(special_option)
    config['SETTINGS']['resume_title'] = resume_title
    config['SETTINGS']['job_desc_title'] = job_desc_title
    config['SETTINGS']['gpt_model'] = gpt_model
    config['SETTINGS']['system_prompt'] = system_prompt
    config['SETTINGS']['temperature'] = str(temperature)
    config['SETTINGS']['max_tokens'] = str(max_tokens)

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    global config_data
    config_data = {
        'folder_path': folder_path,
        'openai_api_key': openai_api_key,
        'hotkey': hotkey,
        'resume_title': resume_title,
        'job_desc_title': job_desc_title,
        'special_option': special_option,
        'gpt_model': gpt_model,
        'system_prompt': system_prompt,
        'temperature': temperature,
        'max_tokens': max_tokens
    }

    return folder_path, openai_api_key, hotkey, special_option, resume_title, job_desc_title, \
        gpt_model, system_prompt, temperature, max_tokens


def get_config(key):
    global config_data
    return config_data.get(key, None)
