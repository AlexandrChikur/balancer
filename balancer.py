import logging
from pathlib import Path

import typer

from balancer import __app_name__ as balancer_name  # type: ignore
from balancer import __version__ as balancer_version  # type: ignore
from balancer.conf.banner import BANNER
from balancer.conf.constants import (
    BALANCER_DEFAULT_LISTENER_PORT,
    BALANCER_DEFAULT_MAX_CONNECTIONS,
)
from balancer.conf.settings import Settings
from balancer.core.balancer import Balancer
from balancer.core.enums import BalancerAlgorithmEnum
from balancer.core.logger import logger
from balancer.utils import create_targets, get_pretty_dict_properties

app = typer.Typer()


def run(
    config: str = typer.Option(...),
    logs: str = typer.Option(
        Path("/var/log/load_balancer"),
        help="Path to directory where logs will be stored",
    ),
    port: int = typer.Option(BALANCER_DEFAULT_LISTENER_PORT),
    max_connections: int = typer.Option(BALANCER_DEFAULT_MAX_CONNECTIONS),
):
    logs_dir = Path(logs)
    if not logs_dir.exists():
        logs_dir.mkdir()  # Means that folder will be created in app folder

    if not logs_dir.is_dir():
        raise ValueError(f"Provided path '{logs}' for logs location is not directory")

    logger_debug_file_handler = logging.FileHandler(
        logs_dir.joinpath(f"{balancer_name}.debug.log")
    )
    logger_debug_file_handler.setLevel(logging.DEBUG)
    logger_debug_file_handler.setFormatter(logger.handlers[0].formatter)

    logger_info_file_handler = logging.FileHandler(
        logs_dir.joinpath(f"{balancer_name}.info.log")
    )
    logger_info_file_handler.setLevel(logging.INFO)
    logger_info_file_handler.setFormatter(logger.handlers[0].formatter)

    logger_err_file_handler = logging.FileHandler(
        logs_dir.joinpath(f"{balancer_name}.err.log")
    )
    logger_err_file_handler.setLevel(logging.ERROR)
    logger_err_file_handler.setFormatter(logger.handlers[0].formatter)

    logger.addHandler(logger_info_file_handler)
    logger.addHandler(logger_debug_file_handler)
    logger.addHandler(logger_err_file_handler)

    path_to_config = Path(config)
    settings = Settings(path_to=path_to_config)
    logger.info(f"Start {balancer_name} v.{balancer_version}" + BANNER)
    logger.info(
        f"With using configuration: {get_pretty_dict_properties(settings.balancer)}"
    )

    targets = create_targets(settings.balancer.targets)

    algorithm = BalancerAlgorithmEnum(settings.balancer.balance_algorithm)
    balancer = Balancer(
        targets=targets, port=port, algorithm=algorithm, max_connections=max_connections
    )
    balancer.run()


if __name__ == "__main__":
    typer.run(run)
