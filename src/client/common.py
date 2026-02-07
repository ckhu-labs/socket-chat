import ipaddress
import sys

BUFFER_SIZE = 1024
TIMEOUT = 5.0

DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = 25535

MESSAGE = (
    "\nEnter a number to check if it's even or odd.\n"
    "Enter 'stop' to shut down the server and client.\n"
    "Press Ctrl+C to exit the client.\n"
)


def config_server() -> tuple[str, int]:
    try:
        while True:
            ip = input(f"Enter server IPv4 address (default: {DEFAULT_IP}): ").strip()
            if not ip:
                server_ip = DEFAULT_IP
                break
            try:
                server_ip = str(ipaddress.IPv4Address(ip))
                break
            except ValueError:
                print("\nEnter a valid IPv4 address.")

        while True:
            port = input(f"Enter server port (default: {DEFAULT_PORT}): ").strip()
            if not port:
                return server_ip, DEFAULT_PORT
            try:
                server_port = int(port)
                # Anything below 1024 is generally reserved for the operating system
                if 1024 <= server_port <= 65535:
                    return server_ip, server_port
                print("\nEnter a valid port number between 1024 and 65535.")
            except ValueError:
                print("\nInvalid input. Enter a numeric value for the port number.")

    except KeyboardInterrupt:
        print("\nClient setup cancelled.")
        sys.exit()
