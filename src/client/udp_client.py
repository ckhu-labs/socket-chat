from socket import AF_INET, SOCK_DGRAM, socket, timeout

from src.client.common import BUFFER_SIZE, MESSAGE, TIMEOUT, config_server


def main():
    server_ip, server_port = config_server()

    with socket(AF_INET, SOCK_DGRAM) as client_socket:
        client_socket.settimeout(TIMEOUT)

        print(f"Client is sending messages to server at {server_ip}:{server_port}.")
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
                    client_socket.sendto(encoded, (server_ip, server_port))
                    data, server = client_socket.recvfrom(BUFFER_SIZE)

                    print(data.decode("utf-8"))

                    if message.lower() == "stop":
                        print(
                            "The server has stopped. The client will also stop running."
                        )
                        break
                except timeout:
                    print("Server did not respond. (timeout)")
        except KeyboardInterrupt:
            print("\nStopping client...")


if __name__ == "__main__":
    main()
