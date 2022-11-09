import multiprocessing
import select
import signal
import socket
import sys
import time

from balancer.conf.constants import (
    BALANCE_DEFAULT_GRACEFUL_SHUTDOWN_TIME,
    BALANCER_DEFAULT_BUFFER_SIZE,
)
from balancer.core.logger import logger


class Worker(multiprocessing.Process):
    """
    A class which handles the worker-side of processing a request
    (communicating between the back-end worker and the requesting client)
    """

    def __init__(
        self,
        host: str,
        port: int,
        client_socket: socket.socket,
        client_host: str,
        buffer_size: int = BALANCER_DEFAULT_BUFFER_SIZE,
    ) -> None:
        super(Worker, self).__init__()
        self.client_socket = client_socket
        self.client_host = client_host

        self.host = host
        self.port = port

        self.worker_socket = None
        self.buffer_size = buffer_size
        self.failure_connection = multiprocessing.Value("i", 0)

    def close_connections(self):
        """
        It closes the client and worker sockets, and then sets the default signal handler for SIGTERM
        """
        logger.info(
            f"Closing connections from '{self.client_socket.getsockname()}' to '{self.worker_socket.getsockname()}' ..."
        )
        try:
            self.worker_socket.shutdown(socket.SHUT_RDWR)
        except Exception as exc:
            logger.exception(exc)
        try:
            self.worker_socket.close()
        except Exception as exc:
            logger.exception(exc)
        try:
            self.client_socket.shutdown(socket.SHUT_RDWR)
        except Exception as exc:
            logger.exception(exc)
        try:
            self.client_socket.close()
        except Exception as exc:
            logger.exception(exc)
        logger.info("Connections closed successfully")
        signal.signal(signal.SIGTERM, signal.SIG_DFL)

    def close_connections_and_shutdown(self, *args):
        """
        It closes all connections and shuts down the program
        """
        self.close_connections()
        sys.exit(0)

    def run(self):
        """
        It reads data from the client socket and sends it to the worker socket, and vice versa
        :return: The data that is being returned is the data that is being sent to the client.
        """
        self.worker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.worker_socket.connect((self.host, self.port))
            logger.info(f"Connected to {self.host}:{self.port}")
        except Exception:
            logger.exception(f"Couldn't connect to the worker {self.host}:{self.port}")
            self.failure_connection.value = 1
            time.sleep(
                BALANCE_DEFAULT_GRACEFUL_SHUTDOWN_TIME
            )  # Give a few seconds for up before it will be removed by the joining thread
            return

        signal.signal(signal.SIGTERM, self.close_connections_and_shutdown)

        try:
            data_snd = b""  # Send to client data
            data_rcv = b""  # Data received from client
            while True:
                waiting_for_write = []
                if data_snd:
                    waiting_for_write.append(self.client_socket)
                if data_rcv:
                    waiting_for_write.append(self.worker_socket)
                try:
                    (read, write, err) = select.select(
                        [self.client_socket, self.worker_socket],
                        waiting_for_write,
                        [self.client_socket, self.worker_socket],
                        0.3,
                    )
                except KeyboardInterrupt:
                    break
                if err:
                    break
                if self.client_socket in read:
                    next_data = self.client_socket.recv(self.buffer_size)
                    if not next_data:
                        break
                    data_rcv += next_data

                if self.worker_socket in read:
                    next_data = self.worker_socket.recv(self.buffer_size)
                    if not next_data:
                        break
                    data_snd += next_data

                if self.worker_socket in write:
                    while data_rcv:
                        self.worker_socket.send(data_rcv[: self.buffer_size])
                        data_rcv = data_rcv[self.buffer_size:]  # fmt: skip

                if self.client_socket in write:
                    while data_snd:
                        self.client_socket.send(data_snd[: self.buffer_size])
                        data_snd = data_snd[self.buffer_size:]  # fmt: skip
            logger.debug(f"Data to send: {data_snd}")
            logger.debug(f"Data to receive: {data_rcv}")
        except Exception as exc:
            logger.critical(
                "Got unexpected behaviour on: %s:%d. Closing connections and shutting down."
                % (self.host, self.port)
            )
            logger.exception(exc)
        self.close_connections_and_shutdown()

    def __str__(self):
        return f"<{__class__.__name__} on={self.host}:{self.port}, from={f'%s:%d' % self.client_socket.getsockname()}>"
