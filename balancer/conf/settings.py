from pathlib import Path

from dynaconf import Dynaconf, Validator  # type: ignore

from balancer.core.enums import BalancerAlgorithmEnum


class Settings:
    """
    Implementation of OSM (Object Settings Mapper).
    It's a wrapper for dynaconf that validates the configuration file.
    The class is a wrapper for dynaconf, which is a library that allows you to load configuration files in a variety of
    formats. The class also validates the configuration file using dynaconf's validators
    Supports configurations according to supported "dynaconf" config types.
    See https://www.dynaconf.com/#features
    """

    __DYNACONF_VALIDATORS = [  # https://www.dynaconf.com/validation/
        Validator(
            "balancer.balance_algorithm",
            condition=BalancerAlgorithmEnum.is_valid_algorithm,
            default=BalancerAlgorithmEnum.ROUND_ROBIN.value,
        ),
        Validator("balancer.targets", must_exist=True),
    ]

    def __init__(self, path_to: Path) -> None:
        self.__dynaconf = Dynaconf(
            settings_files=[path_to], validators=[*self.__DYNACONF_VALIDATORS]
        )
        self.__dynaconf.validators.validate_all()

    def __getattr__(self, *args, **kwargs):
        """Override method for interact with dynaconf as Settings class instance"""
        return self.__dynaconf.__getattr__(*args, **kwargs)
