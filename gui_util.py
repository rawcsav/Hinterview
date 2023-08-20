import os
from colorama import Fore, Style


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def display_intro():
    clear_screen()
    print(Style.BRIGHT + Fore.CYAN + "╔════════════════════════════════════════════════════════════════════════╗")
    print(
        Style.BRIGHT + Fore.CYAN + "║" + Fore.GREEN + "                 Welcome to the Interview Assistant.                    " + Fore.CYAN + "║")
    print(Style.BRIGHT + Fore.CYAN + "╚════════════════════════════════════════════════════════════════════════╝")


def display_instructions():
    print("\nPress and hold the hotkey to record a segment of your interview.")
    print("Release the key to stop recording and get insights.")
    print(Fore.CYAN + "\n──────────────────────────────────────────────────────────────────────────")


def display_footer():
    print(Fore.CYAN + "\n──────────────────────────────────────────────────────────────────────────")
    print("Press and hold the hotkey to record. Release to process.")


def display_recording():
    print(Fore.YELLOW + "\n[STATUS] Recording...")


def display_transcribing():
    print(Fore.BLUE + "[STATUS] Transcribing...")


def display_processing():
    print(Fore.MAGENTA + "[STATUS] Fetching AI Response...")


def display_error(error_message):
    print(Fore.CYAN + "\n──────────────────────────────────────────────────────────────────────────")
    print(Fore.RED + "\nError:", error_message)
