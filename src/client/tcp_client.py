import ipaddress
import logging
from socket import AF_INET, SOCK_STREAM, socket, timeout

BUFFER_SIZE = 2048
TIMEOUT_SECONDS = 5.0

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def get_server_info() -> tuple[str, int]:
    """Gets the server IPv4 and port from the user."""
    while True:
        try:
            server_ip = input("Enter server IPv4 address: ").strip()
            # Validate IPv4 address format
            ipaddress.IPv4Address(server_ip)
            break
        except ValueError:
            print("Invalid IPv4 address format. Please enter a valid IPv4 address.\n")
        except KeyboardInterrupt:
            logger.warning("\nClient startup cancelled.")
            exit(0)

    while True:
        try:
            port = int(input("Enter server port: "))
            if 1024 <= port <= 65535:
                return server_ip, port
            print("Port must be between 1024 and 65535. Please try again.\n")
        except ValueError:
            print("You have not entered a valid port number. Please try again.\n")
        except KeyboardInterrupt:
            logger.warning("\nClient startup cancelled.")
            exit(0)


def main():
    server_ip, server_port = get_server_info()

    # Create TCP socket
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.settimeout(TIMEOUT_SECONDS)

    # Connect to server
    try:
        logger.info("Connecting to server at %s:%d...", server_ip, server_port)
        client_socket.connect((server_ip, server_port))
        print("Successfully connected to server!")
    except timeout:
        logger.error("Connection timeout. Server is not reachable.")
        client_socket.close()
        return
    except ConnectionRefusedError:
        logger.error("Connection refused. Server may not be running.")
        client_socket.close()
        return
    except OSError as e:
        logger.error("Connection error: %s", e)
        client_socket.close()
        return

    print("\nEnter a number to check if it's even or odd.")
    print("Enter 'stop' to shut down the server and client.")
    print("Press Ctrl+C to exit the client.\n")

    try:
        while True:
            message = input("Enter a number: ")

            if not message:
                continue

            if len(message.encode()) > BUFFER_SIZE:
                logger.warning(
                    f"Message length: %d, expected {BUFFER_SIZE}.",
                    len(message.encode()),
                )
                print("Your input was too long. Please try again.")
                continue

            try:
                # Send message to server
                client_socket.sendall(message.encode("utf-8"))

                # Receive response from server
                data = client_socket.recv(BUFFER_SIZE)

                # Check if connection was closed
                if not data:
                    logger.warning("Server closed the connection.")
                    break

                response = data.decode("utf-8")
                print(f"{response}\n")

                # Check if we sent stop command
                if message.lower() == "stop":
                    logger.warning("Server shutdown command sent. Exiting client.")
                    break

            except timeout:
                logger.error(
                    "Server did not respond within %d seconds.", TIMEOUT_SECONDS
                )
                print("Connection timeout. Server may be busy.\n")
            except UnicodeDecodeError:
                logger.error("Received malformed data from server.")
                print("Invalid response from server.\n")
            except ConnectionResetError:
                logger.error("Connection reset by server.")
                print("Server closed the connection unexpectedly.\n")
                break
            except BrokenPipeError:
                logger.error("Connection broken. Server may have shut down.")
                break
            except OSError as e:
                logger.error("Socket error: %s", e)
                print(f"Network error occurred: {e}\n")
                break

    except KeyboardInterrupt:
        logger.warning("\nStopping client...")
    finally:
        client_socket.close()


if __name__ == "__main__":
    main()
