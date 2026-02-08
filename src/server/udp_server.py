from socket import AF_INET, SOCK_DGRAM, socket

from src.server.common import (
    BUFFER_SIZE,
    config_port,
    logger,
    process_message,
    stop_server,
)


def main():
    server_port = config_port()

    with socket(AF_INET, SOCK_DGRAM) as server_socket:
        server_socket.bind(("", server_port))

        logger.info("Server listening on 0.0.0.0:%d", server_port)

        try:
            shutdown = False
            while not shutdown:
                data, client = server_socket.recvfrom(BUFFER_SIZE)

                try:
                    try:
                        message = data.decode("utf-8").strip()
                    except UnicodeDecodeError:
                        logger.warning(
                            "Received invalid message from [%s:%d]: %s", *client, data
                        )
                        response = "Invalid message format. Please send a valid UTF-8 encoded string."
                        server_socket.sendto(response.encode("utf-8"), client)
                        continue

                    logger.info("Received message from [%s:%d]: %s", *client, message)

                    response = process_message(message)
                    server_socket.sendto(response.encode("utf-8"), client)
                    logger.info("Sent response to [%s:%d]: %s", *client, response)

                    if stop_server(message):
                        logger.warning("Received stop command. Shutting down server...")
                        shutdown = True
                except Exception as e:
                    logger.error(
                        "Error processing message from [%s:%d]: %s", *client, e
                    )
        except KeyboardInterrupt:
            logger.warning("\nStopping server...")
        except Exception as e:
            logger.error("Server error: %s", e)


if __name__ == "__main__":
    main()
