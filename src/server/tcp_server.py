import logging
import sys
from socket import AF_INET, SO_REUSEADDR, SOCK_STREAM, SOL_SOCKET, socket

from src.utils.message import BUFFER_SIZE, process

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
            if 1024 <= port <= 65535:
                return port
            print("Port must be between 1024 and 65535. Please try again.\n")
        except ValueError:
            print("You have not entered a valid port number. Please try again.\n")
        except KeyboardInterrupt:
            sys.exit(0)


def handle_client(connection_socket: socket, client_address: tuple[str, int]) -> bool:
    """
    Handle a single client connection.
    Returns True if server should continue, False if shutdown requested.
    """
    logger.info("Connection established with [%s:%d]", *client_address)

    try:
        while True:
            # Receive data from client
            data = connection_socket.recv(BUFFER_SIZE)

            # Check if client disconnected (empty data)
            if not data:
                logger.info("Client [%s:%d] disconnected.", *client_address)
                break

            try:
                message = data.decode("utf-8").strip()
            except UnicodeDecodeError:
                logger.warning(
                    "Received malformed data from [%s:%d], ignoring.", *client_address
                )
                continue

            logger.info("Received from [%s:%d]: %s", *client_address, message)

            # Process the message
            response, should_shutdown = process(message)

            # Send response back to client
            try:
                connection_socket.sendall(response.encode("utf-8"))
                logger.info("Sent to [%s:%d]: %s", *client_address, response)
            except OSError as e:
                logger.error(
                    "Failed to send response to [%s:%d]: %s", *client_address, e
                )
                break

            # Check if shutdown was requested
            if should_shutdown:
                logger.warning("Received stop command from [%s:%d].", *client_address)
                return False

    except ConnectionResetError:
        logger.warning("Connection reset by client [%s:%d]", *client_address)
    except OSError as e:
        logger.error("Connection error with [%s:%d]: %s", *client_address, e)
    finally:
        connection_socket.close()
        logger.info("Connection closed with [%s:%d]", *client_address)

    return True


def main():
    server_port = get_server_port()
    server_socket = socket(AF_INET, SOCK_STREAM)
    # Allow immediate port reuse (helpful during testing)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # SOL_SOCKET, SO_REUSEADDR
    server_socket.bind(("", server_port))

    # Start listening for connections (max 5 queued connections)
    server_socket.listen(5)

    logger.info("TCP Server listening on 0.0.0.0:%d", server_port)
    logger.info("Waiting for client connections...")

    try:
        while True:
            # Accept incoming connection (blocking call)
            connection_socket, client_address = server_socket.accept()

            # Handle the client connection
            should_continue = handle_client(connection_socket, client_address)

            if not should_continue:
                logger.warning("Shutting down server...")
                break

    except KeyboardInterrupt:
        logger.warning("\nStopping server...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
