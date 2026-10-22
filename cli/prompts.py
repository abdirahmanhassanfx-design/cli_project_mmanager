"""Line input and menu choice handling."""

from rich.console import Console
from rich.markup import escape

from cli.display import print_error
from utils.exceptions import NotFoundError, ValidationError


def read_line(console: Console, prompt: str) -> str:
    """Read one line. A closed input stream ends the application."""
    try:
        return console.input(prompt).strip()
    except EOFError:
        raise


def pause(console: Console) -> None:
    """Wait so the administrator can read the last result."""
    read_line(console, "\n[dim]Press Enter to continue...[/dim]")


def ask_menu_choice(console: Console, maximum: int) -> str:
    """Keep asking until the choice is a menu number."""
    while True:
        choice = read_line(console, "[bold]Select an option:[/bold] ")
        if choice in {str(number) for number in range(1, maximum + 1)}:
            return choice
        print_error(
            console,
            f"Invalid choice. Please select an option from 1 to {maximum}.",
        )


def ask_text(console: Console, label: str, parser, default: str | None = None):
    """Ask for a value until ``parser`` accepts it.

    When ``default`` is set, pressing Enter keeps that value. Parser errors
    are shown immediately so a typo does not leave the form.
    """
    while True:
        if default is None:
            prompt = f"[bold]{label}:[/bold] "
            entered = read_line(console, prompt)
        else:
            prompt = f"[bold]{label}[/bold] \\[{escape(default)}]: "
            entered = read_line(console, prompt)
            if entered == "":
                entered = default
        try:
            return parser(entered)
        except (ValidationError, NotFoundError) as exc:
            print_error(console, str(exc))
