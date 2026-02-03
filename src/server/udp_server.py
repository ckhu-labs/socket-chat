from socket import *
from datetime import datetime

while True:
    try:
        server_port = int(input("Enter your server port: "))
        break
    except ValueError:
        print("You have not entered valid port number. Please try again.")

server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(("", server_port))

print(f"\nServer listening on port: {server_port}\n")

try:
    while True:
        data, client = server_socket.recvfrom(2048)
        message = data.decode()

        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        print(f"{timestamp} | Received message from [{client[0]}:{client[1]}]: {message}")

        if message.lower() == "stop":
            print("\nReceived stop command. Shutting down server...")
            response = "The server has shut down."

            server_socket.sendto(response.encode(), client)
            break

        if message.isdigit():
            number = int(message)
            response = "The number you've entered is even.\n" if number % 2 == 0 else "The number you've entered is odd.\n"
        else:
            response = "You have not entered a number. Please try again.\n"

        server_socket.sendto(response.encode(), client)
except KeyboardInterrupt:
    print("\nStopping server...")
finally:
    server_socket.close()
