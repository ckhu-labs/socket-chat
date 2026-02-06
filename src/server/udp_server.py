import logging
import sys
from socket import AF_INET, SOCK_DGRAM, socket

BUFFER_SIZE = 2048

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def get_server_port() -> int:
    """Gets a user-defined port value between 1024 and 65535."""
    while True:
        try:
            port = int(input("Enter your server port: "))
            # Ports below 1024 are usually reserved for the OS
            if 1024 <= port <= 65535:
                return port
            print("Port must be between 1024 and 65535. Please try again.\n")
        except ValueError:
            print("You have not entered a valid port number. Please try again.\n")
        except KeyboardInterrupt:
            sys.exit(0)


def process_message(message: str) -> tuple[str, bool]:
    """Returns (response, should_shutdown)."""
    if message.lower() == "stop":
        return "The server has shut down.", True

    try:
        number = int(message)
        parity = "even" if number % 2 == 0 else "odd"
        return f"The number you entered is {parity}.", False
    except ValueError:
        return "You have not entered a number. Please try again.", False


def main():
    server_port = get_server_port()
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(("", server_port))

    logger.info("Server listening on 0.0.0.0:%d", server_port)

    try:
        while True:
            data, client = server_socket.recvfrom(BUFFER_SIZE)

            try:
                message = data.decode("utf-8").strip()
            except UnicodeDecodeError:
                logger.warning(
                    "Received malformed data from [%s:%d], ignoring.", *client
                )
                continue

            logger.info("Received message from [%s:%d]: %s", *client, message)

            response, should_shutdown = process_message(message)

            try:
                server_socket.sendto(response.encode("utf-8"), client)
            except OSError as e:
                logger.error("Failed to send response to [%s:%d]: %s", *client, e)
                if should_shutdown:
                    break
                continue

            if should_shutdown:
                logger.warning("Received stop command. Shutting down server.")
                break
    except KeyboardInterrupt:
        logger.warning("Stopping server...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
