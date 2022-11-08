from typing import Dict, List, Union

from balancer.core.common.target import Target


def create_targets(dict_target: Dict[str, Dict[str, Union[str, int]]]) -> List[Target]:
    """
    It takes a dictionary of dictionaries and returns a list of `Target` objects

    :param dict_target: Dict[str, Dict[str, Union[str, int]]]
    :type dict_target: Dict[str, Dict[str, Union[str, int]]]
    :return: A list of targets
    """
    targets = []
    for target_name, target_props in dict_target.items():
        targets.append(Target(name=target_name, host=target_props["host"], port=target_props["port"]))  # type: ignore

    return targets


def get_pretty_dict_properties(dict_: Dict[str, str], depth: int = 1) -> str:
    """
    It takes a dictionary and returns a string with the keys and values of the dictionary in a pretty format

    :param dict_: The dictionary to be printed
    :type dict_: Dict[str, str]
    :param depth: The depth of the dictionary. It's amount of "tabs", defaults to 1
    :type depth: Optional[int] (optional)
    :return: A string with the keys and values of the dictionary.
    """

    row = "\t" * depth + "{key}{eq_sign}{value}\n"
    msg = "\n{}"

    rows = []
    for k, v in dict_.items():
        if isinstance(v, dict):
            rows.append(
                row.format(
                    key=k,
                    eq_sign=": ",
                    value=get_pretty_dict_properties(v, depth=depth + 1),
                )
            )
        else:
            rows.append(row.format(key=k, eq_sign=" = ", value=v if v else None))

    return msg.format("".join(rows)).rstrip("\n")
