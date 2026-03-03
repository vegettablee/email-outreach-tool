# this function is what is called when this project is ran, it just handles the entry point of the app
# the reason i put a separate file is just in case i want to do add other functionality on the initial
# opening each time

def start():
    """
    Entry point for the automation-agent CLI application.
    Starts the interactive REPL shell.
    """
    from src.TUI.shell import main as shell_main

    # Initialize and start the TUI shell
    shell_main()


if __name__ == "__main__":
    start() 