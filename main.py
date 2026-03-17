# this function is what is called when this project is ran, it just handles the entry point of the app
# the reason i put a separate file is just in case i want to do add other functionality on the initial
# opening each time

import os
from pathlib import Path

def start():
    """
    Entry point for the automation-agent CLI application.
    Starts the interactive REPL shell.
    """
    # Load environment variables from .env file
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent / '.env'
        load_dotenv(dotenv_path=env_path)
        print(f"Loaded environment variables from {env_path}")
    except ImportError:
        print("Warning: python-dotenv not installed. Environment variables from .env file will not be loaded.")
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")

    from src.TUI.shell import main as shell_main

    # Initialize and start the TUI shell
    shell_main()


if __name__ == "__main__":
    start() 