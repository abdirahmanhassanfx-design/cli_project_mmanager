"""Submenu loop shared by each section of the CLI."""

from cli.display import print_error, show_menu
from cli.prompts import ask_menu_choice, pause
from utils.exceptions import NotFoundError, StorageError, ValidationError


def run_menu(app, title: str, actions: list[tuple[str, object]]) -> None:
    """Show a menu until the administrator chooses the Back item.

    ``actions`` is an ordered list of labels and handlers. A handler of None
    means Back.
    """
    while True:
        show_menu(app.console, title, [label for label, _handler in actions])
        choice = ask_menu_choice(app.console, len(actions))
        _label, handler = actions[int(choice) - 1]
        if handler is None:
            return
        try:
            handler(app)
        except (ValidationError, NotFoundError, StorageError, ValueError, KeyError) as exc:
            print_error(app.console, str(exc))
        pause(app.console)
