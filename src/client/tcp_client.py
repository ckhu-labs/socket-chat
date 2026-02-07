from socket import AF_INET, SOCK_STREAM, socket, timeout

from src.client.common import BUFFER_SIZE, MESSAGE, TIMEOUT, config_server


def main():
    server_ip, server_port = config_server()

    with socket(AF_INET, SOCK_STREAM) as client_socket:
        client_socket.settimeout(TIMEOUT)

        try:
            print(f"Connecting to server at {server_ip}:{server_port}...")
            client_socket.connect((server_ip, server_port))
            print("Successfully connected to server.")
        except (timeout, ConnectionRefusedError):
            print(
                "Connection timeout: server is not reachable. The client will now exit."
            )
            return

        print(MESSAGE)
        try:
            while True:
                message = input("Enter a number: ").strip()

                if not message:
                    continue

                encoded = message.encode("utf-8")
                if len(encoded) > BUFFER_SIZE:
                    print(
                        f"Message length: {len(encoded)}, max allowed: {BUFFER_SIZE}."
                    )
                    print("Your input was too long. Please try again.")
                    continue

                try:
                    client_socket.sendall(encoded)
                    data = client_socket.recv(BUFFER_SIZE)

                    if not data:
                        print("Server closed the connection.")
                        break

                    print(data.decode("utf-8"))

                    if message.lower() == "stop":
                        print(
                            "The server has stopped. The client will also stop running."
                        )
                        break
                except timeout:
                    print(
                        f"Server did not respond within {TIMEOUT} seconds.\nConnection timeout. Server may be busy.\n"
                    )
                except OSError as e:
                    print(f"Network error occurred: {e}\n")
                    break
        except KeyboardInterrupt:
            print("\nStopping client...")


if __name__ == "__main__":
    main()
