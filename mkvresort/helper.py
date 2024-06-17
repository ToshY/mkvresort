import collections
import json
from collections import defaultdict
from pathlib import Path
from rich.traceback import install

install()


def files_in_dir(path: Path, file_types=["*.mkv"]):
    """
    Returns a list of files in the specified directory that match the given file types.

    Args:
        path (Path): The path to the directory.
        file_types (List[str], optional): A list of file types to match. Defaults to ["*.mkv"].

    Returns:
        List[Path]: A list of Path objects representing the files in the directory that match the given file types.
    """

    flist = [f for f_ in [path.rglob(e) for e in file_types] for f in f_]

    return flist


def read_json(path: Path) -> dict:
    """
    Reads a JSON file from the given path and returns its contents as a dictionary.

    Parameters:
        path (Path): The path to the JSON file.

    Returns:
        dict: The contents of the JSON file as a dictionary.
    """

    with path.open("r") as file:
        data = json.load(file)

    return data


def find_in_dict(input_list: list, key: str, value: str):
    """
    Find the index of the first occurrence of a dictionary with a specific key-value pair in a list of dictionaries.

    Parameters:
        input_list (list): A list of dictionaries.
        key (str): The key to search for in the dictionaries.
        value (str): The value to match with the key.

    Returns:
        int or bool: The index of the first occurrence of the dictionary with the specified key-value pair, or False if no match is found.
    """

    for i, dic in enumerate(input_list):
        if dic[key] == value:
            return i

    return False


def split_list_of_dicts_by_key(
    list_of_dicts: list, key: str = "codec_type"
) -> tuple[list[list], list]:
    """
    Splits a list of dictionaries into sublists based on a specified key.

    Parameters:
        list_of_dicts (list): A list of dictionaries to be split.
        key (str, optional): The key to use for splitting. Defaults to "codec_type".

    Returns:
        list: A list of sublists, where each sublist contains dictionaries with the same value for the specified key.
        list: A list of unique values for the specified key.

    """

    result = collections.defaultdict(list)
    keys = []
    for d in list_of_dicts:
        result[d[key]].append(d)
        if d[key] not in keys:
            keys.append(d[key])

    return list(result.values()), keys


def combine_batches(*lists):
    combined = defaultdict(dict)

    for lst in lists:
        for item in lst:
            batch = item["batch"]
            combined[batch].update(item)

    # Convert defaultdict back to a list of dictionaries
    result = [value for key, value in combined.items()]

    return result
