from socket import AF_INET, SO_REUSEADDR, SOCK_STREAM, SOL_SOCKET, socket

from src.server.common import (
    BUFFER_SIZE,
    config_port,
    logger,
    process_message,
    stop_server,
)

MAX_CONNECTIONS = 1


def main():
    server_port = config_port()

    with socket(AF_INET, SOCK_STREAM) as server_socket:
        server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_socket.bind(("", server_port))
        server_socket.listen(MAX_CONNECTIONS)

        logger.info("Server listening on 0.0.0.0:%d", server_port)
        logger.info("Waiting for client connections...")

        try:
            shutdown = False
            while not shutdown:
                conn, client = server_socket.accept()
                logger.info("Connection established with %s:%d", *client)

                try:
                    with conn:
                        while True:
                            data = conn.recv(BUFFER_SIZE)
                            if not data:
                                logger.info("Client %s:%d disconnected.", *client)
                                break

                            try:
                                message = data.decode("utf-8").strip()
                            except UnicodeDecodeError:
                                logger.warning(
                                    "Received invalid message from [%s:%d]: %s",
                                    *client,
                                    data,
                                )
                                response = "Invalid message format. Please send a valid UTF-8 encoded string."
                                conn.sendall(response.encode("utf-8"))
                                continue

                            logger.info(
                                "Received message from %s:%d: %s", *client, message
                            )

                            response = process_message(message)
                            conn.sendall(response.encode("utf-8"))
                            logger.info("Sent response to %s:%d: %s", *client, response)

                            if stop_server(message):
                                logger.warning(
                                    "Received stop command. Shutting down server..."
                                )
                                shutdown = True
                                break
                except Exception as e:
                    logger.error("Error processing message from %s:%d: %s", *client, e)
        except KeyboardInterrupt:
            logger.warning("\nStopping server...")
        except Exception as e:
            logger.error("Server error: %s", e)


if __name__ == "__main__":
    main()
