import multiprocessing
import os
import signal
import socket
import sys
import threading
import time
from typing import List

from balancer.conf.constants import (
    BALANCER_DEFAULT_BIND_RETRY_WAITING,
    BALANCER_DEFAULT_BUFFER_SIZE,
    BALANCER_DEFAULT_CLEANUP_WAITING,
    BALANCER_DEFAULT_LISTENER_HOST,
    BALANCER_DEFAULT_LISTENER_PORT,
    BALANCER_DEFAULT_MAX_CONNECTIONS,
)
from balancer.core.common.algorithms import BalanceAlgorithmFactory
from balancer.core.common.target import Target, TargetAlgorithmizedList
from balancer.core.common.worker import Worker
from balancer.core.enums import BalancerAlgorithmEnum
from balancer.core.logger import logger


class Balancer(multiprocessing.Process):
    """
    Class that listens connections on a local port.
    It's aims to balance a loading between provided targets.
    """

    def __init__(
        self,
        targets: List[Target],
        port: int = BALANCER_DEFAULT_LISTENER_PORT,
        buffer_size: int = BALANCER_DEFAULT_BUFFER_SIZE,
        max_connections: int = BALANCER_DEFAULT_MAX_CONNECTIONS,
        algorithm: BalancerAlgorithmEnum = BalancerAlgorithmEnum.ROUND_ROBIN,
    ) -> None:

        # multiprocessing.Process.__init__(self)
        super(Balancer, self).__init__()

        if type(port) is not int:
            raise TypeError(
                f"Invalid type of 'port' argument, got: {type(port)}. Expected: {int}"
            )

        self.host = BALANCER_DEFAULT_LISTENER_HOST
        self.port = port
        self.algorithm = algorithm
        self.targets = TargetAlgorithmizedList()
        self.targets.attach_algorithm(BalanceAlgorithmFactory.build(self.algorithm))
        self.buffer_size = buffer_size
        self.max_connections = max_connections

        for target in targets:
            self.targets.append(target)
            logger.info(f"Add target: {target} for load distribution")

        self.processing_workers: List[Worker] = []  # Workers currently processing a job
        self.listen_socket: socket.socket = None  # type: ignore        # Socket for incoming connections
        self.cleanup_thread: threading.Thread = None  # type: ignore    # Cleans up completed workers
        self.keep_going: bool = (
            True  # Turns to False when the application is set to terminate
        )

        logger.info("Balancer initialization: %s completed successfully" % self)

    def cleanup(self):
        """
        It waits for a certain amount of time, then checks if any of the workers are done. If they are, it removes them from
        the list of workers
        """
        logger.info(f"Cleaning up will start in {BALANCER_DEFAULT_CLEANUP_WAITING}s...")
        time.sleep(BALANCER_DEFAULT_CLEANUP_WAITING)  # Wait for things to kick off
        while self.keep_going is True:
            processing_workers_copy = self.processing_workers[:]
            for worker in processing_workers_copy:
                if worker.is_alive() is False:  # Worker is done
                    self.processing_workers.remove(worker)
                    logger.info(f"Worker '{worker}' is successfully cleaned up")

    def close_workers(self):
        """
        It closes the listening socket, then it tries to terminate all the workers, and if they don't terminate, it kills
        them
        """
        self.keep_going = False
        try:
            self.listen_socket.shutdown(socket.SHUT_RDWR)
        except Exception as exc:
            logger.exception(exc)
        try:
            self.listen_socket.close()
        except Exception as exc:
            logger.exception(exc)

        if not self.processing_workers:
            self.cleanup_thread and self.cleanup_thread.join(3)
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            sys.exit(0)

        for worker in self.processing_workers:
            try:
                worker.terminate()
                os.kill(worker.pid, signal.SIGTERM)  # type: ignore
                logger.warning(f"Worker '{worker}' is terminated")
            except Exception as exc:
                logger.exception(exc)

        remaining_workers = []
        for worker in self.processing_workers:
            worker.join(0.03)
            if worker.is_alive() is True:  # Worker still in execution
                remaining_workers.append(worker)

        if len(remaining_workers) > 0:
            # One last chance to complete, then we kill
            for worker in remaining_workers:
                worker.join(0.2)

        self.cleanup_thread and self.cleanup_thread.join(2)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        sys.exit(0)

    def retry_failed_workers(self):
        """
        retry_failed_workers -
            This method loops over current running workers and scans them for a multiprocess shared field called "failure_connection".
            If this is set to 1, then we failed to connect to the backend worker.
            If that happens, it goes pick a different target and use worker to handle it.
        """

        not_failed = 0  # We use this to differ between long waits in between successful periods and short waits when there is a failing host in the mix.
        while self.keep_going is True:
            processing_workers_copy = self.processing_workers[:]
            for worker in processing_workers_copy:
                if worker.failure_connection.value == 1:
                    target = self.__next_target()
                    while target.host == worker.host and target.port == target.port:
                        # Make sure the newly selected target is not the one we are changing
                        target = self.__next_target()

                    logger.info(
                        f"Retry client '{worker.client_host}' request from "
                        f"worker {worker.host}:{worker.port} to "
                        f"another worker: {target.host}:{target.port}"
                    )

                    next_worker = Worker(
                        target.host,
                        target.port,
                        worker.client_socket,
                        worker.client_host,
                        self.buffer_size,
                    )
                    next_worker.start()
                    self.processing_workers.append(next_worker)
                    worker.failure_connection.value = 0  # Reset

            not_failed += 1
            if not_failed > 1000000:  # Make sure we don't overrun
                not_failed = 6
            if not_failed > 5:
                time.sleep(2)
            else:
                time.sleep(0.05)

    def run(self):
        """
        It creates a socket, binds it to the host and port, and then listens for incoming connections.
        When a connection is received, it creates a new worker thread to handle the connection.
        The worker thread is then added to the processing_workers list.
        The worker thread is then started.
        The main thread then loops back to the top of the while loop and waits for the next connection.
        The worker thread is responsible for handling the connection.
        The worker thread is also responsible for removing itself from the processing_workers list when it's done.
        The main thread is responsible for removing the worker thread from the processing_workers list if it's not done in a
        timely manner.
        The main thread is also responsible for removing the worker thread from the processing_workers list if it's done in
        a timely manner.
        The main thread is also responsible for removing the worker thread
        :return: NoReturn
        """
        signal.signal(signal.SIGTERM, self.close_workers)
        while True:
            try:
                listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                except Exception as exc:
                    logger.exception(exc)
                listen_socket.bind((self.host, self.port))
                self.listen_socket = listen_socket
                break
            except Exception:
                logger.exception(
                    f"Failed to bind to {self.host}:{self.port}. Retrying in {BALANCER_DEFAULT_BIND_RETRY_WAITING} seconds ..."
                )
                time.sleep(BALANCER_DEFAULT_BIND_RETRY_WAITING)

        listen_socket.listen(self.max_connections)

        # Create thread that will cleanup completed tasks
        self.cleanup_thread = cleanup_thread = threading.Thread(target=self.cleanup)
        cleanup_thread.start()

        # Create thread that will retry failed tasks
        retry_thread = threading.Thread(target=self.retry_failed_workers)
        retry_thread.start()

        try:
            while self.keep_going is True:
                if self.keep_going is False:
                    break
                try:
                    (client_socket, client_host) = listen_socket.accept()
                except Exception:
                    logger.exception(f"Failed bind to {self.host}:{self.port}")
                    if self.keep_going is True:
                        # Exception did not come from termination process, so keep rollin'
                        time.sleep(3)
                        continue
                    raise  # Termination DID come from termination process, so abort.

                target = self.__next_target()
                new_worker = Worker(
                    target.host,
                    target.port,
                    client_socket,
                    client_host,
                    self.buffer_size,
                )
                self.processing_workers.append(new_worker)
                new_worker.start()

        except Exception as exc:
            logger.critical(
                f"Got unexpected behaviour. Start shutting down workers on: {self.host}:{self.port}"
            )
            logger.exception(exc)
            self.close_workers()
            return

        self.close_workers()

    def __next_target(self) -> Target:
        """
        > This function returns the next target in the list of targets
        :return: The next target in the list.
        """
        return self.targets.get_next()

    def __str__(self):
        return f"<{__class__.__name__} host={self.host} port={self.port} algorithm={self.algorithm.name} targets_amount={len(self.targets)}>"
