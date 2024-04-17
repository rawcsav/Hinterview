import os
from colorama import Fore, Style
from art import *
from config import configure_settings, get_config, configure_file_types
from openai_util import embed_documents

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_intro():
    clear_screen()

    ascii_art = text2art("Hinterview", "slant")

    print(Style.BRIGHT + Fore.CYAN, end="")

    colored_ascii_art = ascii_art.replace("/", Fore.GREEN + "/" + Fore.CYAN)
    colored_ascii_art = colored_ascii_art.replace("_", Fore.GREEN + "_" + Fore.CYAN)

    print(colored_ascii_art)
    print(Fore.CYAN + "──────────────────────────────────────────────────────────────────────────")

def display_initial_menu():
    print(Fore.YELLOW + "1. Start Interview")
    print(Fore.YELLOW + "2. Settings")
    print(Fore.YELLOW + "3. Exit")
    choice = input(Fore.GREEN + "Please select an option (1-3): ")
    return choice

def display_settings_menu():
    clear_screen()
    print(Fore.CYAN + "──────────────────────────────────────────────────────────────────────────")
    print(Style.BRIGHT + Fore.GREEN + "                          SETTINGS")
    print(Fore.YELLOW + "1. Folder Path")
    print(Fore.YELLOW + "2. OpenAI API Key")
    print(Fore.YELLOW + "3. Hotkey")
    print(Fore.YELLOW + "4. GPT Model")
    print(Fore.YELLOW + "5. System Prompt")
    print(Fore.YELLOW + "6. Temperature")
    print(Fore.YELLOW + "7. Top P")
    print(Fore.YELLOW + "8. Max Tokens")
    print(Fore.CYAN + "──────────────────────────────────────────────────────────────────────────")
    print(Fore.GREEN + "0. Save and Return")
    choice = input(Fore.LIGHTGREEN_EX + "Please select an option (0-8): ")
    return choice

def handle_settings_menu():
    while True:
        choice = display_settings_menu()
        if choice == '0':
            print(Fore.GREEN + "Settings saved successfully!")
            break
        elif choice in ('1', '2', '3', '4', '5', '6', '7', '8'):
            settings_options = {
                '1': ('Enter the new folder path (or "b" to go back): ', 'folder_path'),
                '2': ('Enter the new OpenAI API Key (or "b" to go back): ', 'openai_api_key'),
                '3': ('Enter the new hotkey (or "b" to go back): ', 'hotkey'),
                '4': ('Enter the new GPT model (or "b" to go back): ', 'gpt_model'),
                '5': ('Enter the new system prompt (or "b" to go back): ', 'system_prompt'),
                '6': ('Enter the new temperature value (or "b" to go back): ', 'temperature'),
                '7': (
                'Enter the new top_p value (or "b" to go back): ', 'top_p'),
                '8': ('Enter the new max tokens value (or "b" to go back): ', 'max_tokens'),
            }
            prompt, setting_name = settings_options[choice]
            new_value = input(Fore.GREEN + prompt)
            if new_value.lower() == 'b':
                continue
            if setting_name == 'folder_path' and new_value.lower() != 'b' and not os.path.exists(new_value.strip('"')):
                print(Fore.RED + "Invalid folder path. Please enter a valid path.")
            else:
                configure_settings(**{setting_name: new_value})
            clear_screen()
        else:
            print(Fore.RED + "Invalid choice. Please try again.")
def display_instructions():
    print("\nPress and hold the hotkey (default: Option) to record a segment of your interview.")
    print("Release the key to stop recording and get insights.")

def display_recording():
    print(Fore.CYAN + "\n──────────────────────────────────────────────────────────────────────────")
    print(Fore.YELLOW + "\n[STATUS] Recording...")

def display_transcribing():
    print(Fore.BLUE + "[STATUS] Transcribing...")

def display_processing():
    print(Fore.MAGENTA + "[STATUS] Fetching AI Response...")

def display_error(error_message):
    print(Fore.CYAN + "\n──────────────────────────────────────────────────────────────────────────")
    print(Fore.RED + "\nError:", error_message)

def primary_gui():
    display_intro()

    while True:
        choice = display_initial_menu()

        if choice == '1':
            print(Fore.GREEN + "Starting Interview...\n")
            break
        elif choice == '2':
            handle_settings_menu()
        elif choice == '3':
            print(Fore.GREEN + "Exiting...")
            exit()
        else:
            print(Fore.RED + "Invalid choice. Please try again.")

    configure_settings()
    folder_path = get_config("folder_path")
    print("\nCurrent directory path:" + Fore.LIGHTGREEN_EX + Style.BRIGHT + f"{folder_path}\n")

    configure_file_types(folder_path)

    titles, locs, texts, embeddings = embed_documents(folder_path)

    display_instructions()

    return titles, locs, texts, embeddings