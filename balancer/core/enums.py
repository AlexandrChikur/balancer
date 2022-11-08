import enum
from typing import List


class BaseBalancerEnum(enum.Enum):
    """
    It's an enum that can be used to check if a value is in the enum,
    and it can be used to get a list of all the values in the enum
    """

    @classmethod
    def has_value(cls, value) -> bool:
        return value in cls._value2member_map_

    @classmethod
    def values(cls) -> List[str]:
        return list(map(lambda c: c.value, cls))  # type: ignore


@enum.unique
class BalancerAlgorithmEnum(BaseBalancerEnum):
    """Enum class that describes existing balance algorithms"""

    RANDOM = "random"
    ROUND_ROBIN = "round-robin"

    @classmethod
    def is_valid_algorithm(cls, value) -> bool:
        return cls.has_value(value)
