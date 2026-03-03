# registers/initializes all of the commands, gather everything from the workflows and call them
# this is where most rate limiting will take place

from rich.console import Console

console = Console()


class CommandHandler:
    def __init__(self):
        self.commands = {
            "stats": self.show_stats,
            "find_emails": self.find_emails,
            "send_emails": self.send_emails,
            "help": self.show_help,
        }

    def parse(self, user_input):
        """
        Parse user input into command and arguments.
        Simple implementation: first word is command, rest are args.
        """
        parts = user_input.strip().split(maxsplit=1)
        command = parts[0] if parts else ""
        args_str = parts[1] if len(parts) > 1 else ""

        # Parse args into dict (basic implementation)
        args = {}
        if args_str:
            # Simple key=value parsing
            for arg in args_str.split():
                if "=" in arg:
                    key, value = arg.split("=", 1)
                    args[key.lstrip("-")] = value
                else:
                    # Store unnamed args in 'input' key
                    args["input"] = args_str

        return command, args

    def execute(self, user_input):
        """Execute the parsed command."""
        command, args = self.parse(user_input)

        # Route to appropriate handler
        if command in self.commands:
            self.commands[command](args)
        else:
            console.print(f"[red]Unknown command: '{command}'[/red]")
            console.print("[dim]Type 'help' to see available commands[/dim]")

    def show_stats(self, args):
        """Display statistics about emails and companies."""
        console.print("[cyan]Fetching statistics...[/cyan]")

        # TODO: Query database for actual stats
        console.print("\n[bold]Email Statistics:[/bold]")
        console.print("  Emails sent: 0")
        console.print("  Emails pending: 0")
        console.print("  Replies received: 0")
        console.print("\n[bold]Company Statistics:[/bold]")
        console.print("  Companies researched: 0")
        console.print("  Contacts found: 0\n")

    def find_emails(self, args):
        """Research companies and find recruiter emails."""
        console.print("[cyan]Starting email research workflow...[/cyan]")

        # TODO: Call company research agent workflow
        # from src.agents.company_research_agent import research_workflow
        # result = research_workflow(args)

        console.print("[yellow]Note: Research workflow not yet implemented[/yellow]")
        console.print(f"[dim]Args received: {args}[/dim]\n")

    def send_emails(self, args):
        """Send personalized cold emails."""
        console.print("[cyan]Starting email sending workflow...[/cyan]")

        # TODO: Call email agent workflow
        # from src.agents.email_agent import send_email_workflow
        # result = send_email_workflow(args)

        console.print("[yellow]Note: Email workflow not yet implemented[/yellow]")
        console.print(f"[dim]Args received: {args}[/dim]\n")

    def show_help(self, args):
        """Show available commands and usage."""
        console.print("\n[bold cyan]Available Commands:[/bold cyan]\n")
        console.print("[green]stats[/green]")
        console.print("  Display email and company statistics\n")
        console.print("[green]find_emails[/green]")
        console.print("  Research companies and find recruiter emails")
        console.print("  Example: find_emails company=Stripe\n")
        console.print("[green]send_emails[/green]")
        console.print("  Send personalized cold emails")
        console.print("  Example: send_emails recipient=recruiter@company.com\n")
        console.print("[green]help[/green]")
        console.print("  Show this help message\n")
        console.print("[green]exit[/green]")
        console.print("  Exit the automation agent\n")