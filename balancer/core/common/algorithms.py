import random

# from balancer.core.enums import BalancerAlgorithmEnum
from abc import ABCMeta, abstractmethod
from itertools import cycle
from typing import Any, List

from balancer.core.exceptions import WrongBalanceAlgorithmError


class AbstractBalanceAlgorithm(metaclass=ABCMeta):
    @abstractmethod
    def set_sequence(self, seq: List[Any]) -> None:
        """Items sequence setter"""
        raise NotImplementedError("Method should be overridden")

    @abstractmethod
    def get_next_item(self) -> Any:
        """Implement this method with algorithm that should
        return sequence item by described rules"""
        raise NotImplementedError("Method should be overridden")


class RandomBalanceAlgorithm(AbstractBalanceAlgorithm):
    def set_sequence(self, seq: List[Any]) -> None:
        self.sequence = seq

    # A method that returns a random item from the sequence.
    def get_next_item(self) -> Any:
        return random.choice(self.sequence)


class RoundRobinBalanceAlgorithm(AbstractBalanceAlgorithm):
    def set_sequence(self, seq: List[Any]) -> None:
        self.sequence = seq
        self.iter = cycle(self.sequence)

    def get_next_item(self) -> Any:
        return next(self.iter)


#
class BalanceAlgorithmFactory:
    """This class is responsible for building balance algorithms."""

    @staticmethod
    def build(algorithm_type) -> AbstractBalanceAlgorithm:
        """
        "If the algorithm type is random, return a random balance algorithm, if it's round robin, return a round robin
        balance algorithm, otherwise raise an error."

        :param algorithm_type: The type of algorithm to build
        """
        try:
            match algorithm_type:
                case algorithm_type.RANDOM:
                    return RandomBalanceAlgorithm()
                case algorithm_type.ROUND_ROBIN:
                    return RoundRobinBalanceAlgorithm()
        except AttributeError:
            raise WrongBalanceAlgorithmError(
                f"Provided algorithm '{algorithm_type}' is invalid"
            )
        raise TypeError(
            f"No found instance to build by provided algorithm type: {algorithm_type}"
        )
