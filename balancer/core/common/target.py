from typing import Any, List, Optional

from balancer.core.common.algorithms import AbstractBalanceAlgorithm
from balancer.core.exceptions import WrongBalanceAlgorithmError


class Target:
    """
    It's a class that represents a target between the set of which the load is distributed
    """

    def __init__(self, name: str, host: str, port: int) -> None:
        if host is None:
            raise ValueError(f"Argument 'host' shouldn't be {None}")
        if port is None:
            raise ValueError(f"Argument 'port' shouldn't be {None}")

        if type(port) is not int:
            raise TypeError(
                f"Invalid type of 'port' argument, got: {type(port)}. Expected: {int}"
            )

        self.__name = name
        self.__host = host
        self.__port = port

    @property
    def name(self) -> str:
        return self.__name

    @property
    def host(self) -> str:
        return self.__host

    @property
    def port(self) -> int:
        return self.__port

    def __str__(self):
        return f"<{__class__.__name__} name={self.__name} host={self.__host} port={self.__port})>"


class TargetAlgorithmizedList(list):
    """
    Target-typed class that aims to have targets and give it by applied algorithm.
    """

    __items_type__ = Target
    __slots__ = (
        "targets",
        "__algorithm",
    )

    def __init__(self, targets: Optional[List[Target]] = None) -> None:
        if targets is not None:
            for t in targets:
                self.append(t)
        self.__algorithm: AbstractBalanceAlgorithm

        super(TargetAlgorithmizedList, self).__init__()

    def attach_algorithm(self, algorithm: AbstractBalanceAlgorithm):
        """It's a method that attaches an algorithm to the list. And set sequence for the algorithm"""
        if not isinstance(algorithm, AbstractBalanceAlgorithm):
            raise WrongBalanceAlgorithmError(
                f"Provided invalid algorithm '{algorithm}'. "
                f"Expected: {AbstractBalanceAlgorithm} (or it's children)"
            )
        self.__algorithm = algorithm
        self.__algorithm.set_sequence(self)

    def append(self, item: Target):
        self.__check_type(item)
        super(TargetAlgorithmizedList, self).append(item)

    def get_next(self):
        return self.__algorithm.get_next_item()

    def __check_type(self, v: Any):
        """Checks if an item is suitable for this class"""
        if not isinstance(v, self.__items_type__):
            raise TypeError(
                "Item is not of type %s. Got %s" % (self.__items_type__, type(v))
            )

    def __setitem__(self, key, value):
        self.__check_type(value)
        super(TargetAlgorithmizedList, self).__setitem__(key, value)
