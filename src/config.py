import configparser
from colorama import init
import os

init(autoreset=True)

config_data = {}

def open_config():
    config = configparser.ConfigParser()

    if os.path.exists('config.ini'):
        config.read('config.ini')
    else:
        config['SETTINGS'] = {
            'folder_path': '',
            'openai_api_key': '',
            'hotkey': 'alt_r',
            'interview_mode': 'True',
            'gpt_model': 'gpt-4',
            'system_prompt': 'You are a knowledgeable job interview assistant that uses information from provided textual excerpts to provide impressive, but concise answers to interview questions.',
            'temperature': '0.5',
            'max_tokens': '1000',
            'resume_title': '',
            'job_desc_title': ''
        }
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    return config

def get_config(key):
    return config_data.get(key, None)
def configure_user_settings():
    config = open_config()

    folder_path = config.get('SETTINGS', 'folder_path')
    openai_api_key = config.get('SETTINGS', 'openai_api_key')
    hotkey = config.get('SETTINGS', 'hotkey')
    interview_mode = config.getboolean('SETTINGS', 'interview_mode')
    resume_title = config.get('SETTINGS', 'resume_title')
    job_desc_title = config.get('SETTINGS', 'job_desc_title')

    # Ask user for folder path
    if not folder_path:
        folder_path = input("Enter directory path for .txt documents: ")

    # Ask user for OpenAI API key
    if not openai_api_key:
        openai_api_key = input("Enter your OpenAI API key: ")

    # Ask user if they want to use the special interview option
    if interview_mode is False:
        response = input("Do you want to use interview mode? (y/n): ")
        interview_mode = True if response.lower() == 'y' else False

    # If special option is enabled, ask for resume and job description titles
    if interview_mode:
        if not resume_title:
            resume_title = input("Enter resume doc title (without the .txt): ")

        if not job_desc_title:
            job_desc_title = input("Enter job description doc title (without the .txt): "  + "\n")

    # Save user settings to config
    config['SETTINGS']['folder_path'] = folder_path
    config['SETTINGS']['openai_api_key'] = openai_api_key
    config['SETTINGS']['hotkey'] = hotkey
    config['SETTINGS']['interview_mode'] = str(interview_mode)
    config['SETTINGS']['resume_title'] = resume_title
    config['SETTINGS']['job_desc_title'] = job_desc_title

    config_data.update({
        'folder_path': folder_path,
        'openai_api_key': openai_api_key,
        'hotkey': hotkey,
        'resume_title': resume_title,
        'job_desc_title': job_desc_title,
        'interview_mode': interview_mode,
    })

    return folder_path, openai_api_key, hotkey, interview_mode, resume_title, job_desc_title


def configure_gpt_settings():
    config = open_config()

    gpt_model = config.get('SETTINGS', 'gpt_model')
    system_prompt = config.get('SETTINGS', 'system_prompt')
    temperature = config.getfloat('SETTINGS', 'temperature')
    max_tokens = config.getint('SETTINGS', 'max_tokens')

    # Save GPT settings to config
    config['SETTINGS']['gpt_model'] = gpt_model
    config['SETTINGS']['system_prompt'] = system_prompt
    config['SETTINGS']['temperature'] = str(temperature)
    config['SETTINGS']['max_tokens'] = str(max_tokens)

    config_data.update({
        'gpt_model': gpt_model,
        'system_prompt': system_prompt,
        'temperature': temperature,
        'max_tokens': max_tokens
    })

    return gpt_model, system_prompt, temperature, max_tokens

def configure_settings(**kwargs):
    config = open_config()
    user_settings = configure_user_settings()
    gpt_settings = configure_gpt_settings()

    # Update the specific setting if provided
    if kwargs:
        for key, value in kwargs.items():
            config['SETTINGS'][key] = value
            config_data[key] = value

    # Save the configuration to a file
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    config_data.update(dict(zip(
        ['folder_path', 'openai_api_key', 'hotkey', 'interview_mode', 'resume_title', 'job_desc_title',
         'gpt_model', 'system_prompt', 'temperature', 'max_tokens'],
        user_settings + gpt_settings
    )))

    return user_settings + gpt_settings
