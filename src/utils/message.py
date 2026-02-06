BUFFER_SIZE = 2048

def process(message: str) -> tuple[str, bool]:
    """Returns (response, should_shutdown)."""
    if message.lower() == "stop":
        return "The server has shut down.", True

    try:
        number = int(message)
        parity = "even" if number % 2 == 0 else "odd"
        return f"The number you entered is {parity}.", False
    except ValueError:
        return "You have not entered a number. Please try again.", False
