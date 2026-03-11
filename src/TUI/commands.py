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
            "clean_raw_data": self.clean_raw_data,
            "create_drafts": self.create_drafts,
            "review_drafts": self.review_drafts,
            "queue_reviewed_emails": self.queue_reviewed_emails,
            "help": self.show_help,
        }

    def parse(self, user_input):
        """
        Parse user input into command and arguments.
        Simple implementation: first word is command, rest are args.
        """
        parts = user_input.strip().split()
        command = parts[0] if parts else ""

        # Parse args into dict (basic implementation)
        args = {}

        if len(parts) > 1:
            # Check if second part is a number (for commands like create_drafts 5)
            try:
                args["count"] = int(parts[1])
            except ValueError:
                # Not a number, try key=value parsing
                args_str = " ".join(parts[1:])
                for arg in parts[1:]:
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
        # two main stats stat functionalities are required
        # overall stats needed via SQL queries: 

        # company emails that have not been sent and uncontacted(check contact status for company and email num_sent = 0)
        # recruiter emails that have not been sent and uncontacted(check contact_status for company AND recruiter, and email num_sent = 0)
        # total emails that have not been sent and uncontacted(check contact_status on email and num_sent = 0)
        # emails that have been replied too(create a separate function that invokes a refresh, for now, just set to 0)
        # 

        # email_session stats needed via email_session.json: 
        # number of drafts
        # number of drafts to review 
        # number of emails queued 
        # TODO: Query database for actual stats
        console.print("\n[bold]Email Statistics:[/bold]")
        console.print("  Emails sent: 0")
        console.print("  Emails pending: 0")
        console.print("  Replies received: 0")
        console.print("\n[bold]Company Statistics:[/bold]")
        console.print("  Companies researched: 0")
        console.print("  Contacts found: 0\n")

    def run_cold_email_workflow(self, args):
        """
        Coordinates create_drafts, review_drafts, queue_reviewed_emails.
        Do after these functions work properly.
        """
        console.print("[cyan]Running full cold email workflow...[/cyan]")
        # TODO: Implement after individual workflows are tested

    def create_drafts(self, args):
        """Create email drafts from database entries."""
        count = args.get("count", 0)
        console.print(f"[cyan]Creating {count} drafts from database...[/cyan]")
        # TODO: Call orchestrator.run_draft_email_workflow(count)

    def review_drafts(self, args):
        """Review draft emails."""
        count = args.get("count", 0)
        console.print(f"[cyan]Fetching {count} drafts for review...[/cyan]")
        # TODO: Call orchestrator.run_review_email_workflow(count)

    def queue_reviewed_emails(self, args):
        """Queue reviewed emails to be sent."""
        count = args.get("count", 0)
        console.print(f"[cyan]Queueing {count} reviewed emails...[/cyan]")
        # TODO: Call orchestrator.run_queue_email_workflow(count)
    
    def clean_raw_data(self, args): # cleans the data.json file, validates the files before starting the email automation workflow 
        console.print("Cleaning data.json file and inserting into DB...")

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
        console.print("[green]create_drafts <count>[/green]")
        console.print("  Create email drafts from database")
        console.print("  Example: create_drafts 5\n")
        console.print("[green]review_drafts <count>[/green]")
        console.print("  Review draft emails")
        console.print("  Example: review_drafts 3\n")
        console.print("[green]queue_reviewed_emails <count>[/green]")
        console.print("  Queue reviewed emails to be sent")
        console.print("  Example: queue_reviewed_emails 2\n")
        console.print("[green]find_emails[/green]")
        console.print("  Research companies and find recruiter emails")
        console.print("  Example: find_emails company=Stripe\n")
        console.print("[green]send_emails[/green]")
        console.print("  Send personalized cold emails")
        console.print("  Example: send_emails recipient=recruiter@company.com\n")
        console.print("[green]clean_raw_data[/green]")
        console.print("  Clean and validate data.json before insertion\n")
        console.print("[green]help[/green]")
        console.print("  Show this help message\n")
        console.print("[green]exit[/green]")
        console.print("  Exit the automation agent\n")