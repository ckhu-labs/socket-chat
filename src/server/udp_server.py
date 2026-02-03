from socket import *

while True:
    try:
        server_port = int(input("Enter your server port: "))
        break
    except ValueError:
        print("You have not entered valid port number. Please try again.")

server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(('' , server_port))

print(f"Listening on port: {server_port}")

while True:
    data, client = server_socket.recvfrom(2048)
    message = data.decode()

    print(f"Received message from [{client[0]}:{client[1]}]: {message}")

    if message.isdigit():
        number = int(message)
        response = "The number you've entered is even.\n" if number % 2 == 0 else "The number you've entered is odd.\n"
    else:
        response = "You have not entered a number. Please try again.\n"

    server_socket.sendto(response.encode(), client)
