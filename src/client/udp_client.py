import ipaddress
import logging
import sys
from socket import AF_INET, SOCK_DGRAM, socket, timeout

BUFFER_SIZE = 2048

logging.basicConfig(
    level=logging.INFO,
    format="\n%(asctime)s | %(levelname)s | %(message)s",
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
            sys.exit(0)

    while True:
        try:
            port = int(input("Enter server port: "))
            if 1024 <= port <= 65535:
                return server_ip, port
            print("Port must be between 1024 and 65535. Please try again.\n")
        except ValueError:
            print("You have not entered a valid port number. Please try again.\n")
        except KeyboardInterrupt:
            sys.exit(0)


def main():
    server_ip, server_port = get_server_info()
    client_socket = socket(AF_INET, SOCK_DGRAM)
    # Add a 5-second timeout if we can't reach the server
    client_socket.settimeout(5.0)

    print("\nEnter a number to check if it's even or odd.")
    print("Enter 'stop' to shut down the server and client.")
    print("Press Ctrl+C to exit the client.\n")

    try:
        while True:
            message = input("\nEnter a number: ")

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
                client_socket.sendto(message.encode("utf-8"), (server_ip, server_port))
                data, server = client_socket.recvfrom(BUFFER_SIZE)

                if server != (server_ip, server_port):
                    logger.warning(f"Unexpected response from {server}, ignoring.")
                    continue

                print(data.decode("utf-8"))

                if message.lower().strip() == "stop":
                    logger.warning(
                        "The server has stopped. The client will also stop running."
                    )
                    break
            except timeout:
                logger.error("Server did not respond. (timeout)")
            except UnicodeDecodeError:
                logger.error("Received malformed data from server, ignoring.")
            except OSError as e:
                logger.error(f"Socket error: {e}")
                break
    except KeyboardInterrupt:
        logger.warning("Stopping client...")
    finally:
        client_socket.close()


if __name__ == "__main__":
    main()
