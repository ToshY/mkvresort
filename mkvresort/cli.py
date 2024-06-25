import click
from mkvresort.process import ProcessCommand
from loguru import logger  # noqa
import json
from pathlib import Path
from mkvresort.args import InputPathChecker, OutputPathChecker, PresetPathChecker
from mkvresort.helper import (
    find_in_dict,
    split_list_of_dicts_by_key,
    combine_arguments_by_batch,
)


def mkvmerge_identify_streams(
    input_file, total_items, item_index, batch_index, batch_name
):
    """
    Identifies the streams in an MKV file using MKVmerge and returns a dictionary of streams sorted by codec type.

    Args:
        input_file (str): The path to the MKV file to identify.
        total_items (int): The total number of items in the batch.
        item_index (int): The index of the current item in the batch.
        batch_index (int): The index of the current batch.
        batch_name (str): The name of the current batch.

    Returns:
        dict: A dictionary of streams sorted by codec type, with the following structure:
            - The keys are the codec types ("video", "audio", "subtitles").
            - The values are dictionaries with two keys:
                - "streams": A dictionary of individual streams, with the following structure:
                    - The keys are the stream IDs.
                    - The values are dictionaries with the stream information.
                - "count": The number of streams of the given codec type.
    """

    if item_index == 0:
        logger.info(
            f"MKVmerge identify batch `{batch_index}` for `{batch_name}` started."
        )

    mkvmerge_identify_command = [
        "mkvmerge",
        "--identify",
        "--identification-format",
        "json",
        str(input_file),
    ]

    process = ProcessCommand(logger)
    result = process.run("MKVmerge identify", mkvmerge_identify_command)

    mkvmerge_identify_output = json.loads(result.stdout)

    # Split by codec_type
    split_streams, split_keys = split_list_of_dicts_by_key(
        mkvmerge_identify_output["tracks"], "type"
    )

    # Rebuild streams & count per codec type
    streams = {k: {"streams": {}, "count": 0} for k in split_keys}
    for x, s in enumerate(split_keys):
        streams[s]["streams"] = split_streams[x]
        streams[s]["count"] = len(streams[s]["streams"])

    # Sort streams to video - audio - subtitles
    streams = {k: streams[k] for k in ["video", "audio", "subtitles"]}

    if item_index == total_items - 1:
        logger.info(
            f"MKVmerge identify batch `{batch_index}` for `{batch_name}` completed."
        )

    return streams


def mkvmerge_resort_streams(
    input_file: Path,
    output_path: Path,
    track_order,
    total_items,
    item_index,
    batch_index,
    batch_name,
    new_file_suffix=" (1)",
):
    """
    Resorts the streams in an MKV file using MKVmerge.

    Args:
        input_file (Path): The path to the MKV file to resort.
        output_path (Path): The path to the output directory.
        track_order (list): The order of the tracks to resort.
        total_items (int): The total number of items in the batch.
        item_index (int): The index of the current item in the batch.
        batch_index (int): The index of the current batch.
        batch_name (str): The name of the current batch.
        new_file_suffix (str, optional): The suffix to add to the output file. Defaults to " (1)".

    Returns:
        None
    """

    if item_index == 0:
        logger.info(
            f"MKVmerge resort streams batch `{batch_index}` for `{batch_name}` started."
        )

    track_order_args = ",".join(["0:" + str(v) for v in track_order])

    # Output extension
    output_extension = ".mkv"

    # Prepare output file name
    if output_path.is_dir():
        output_file = str(
            output_path.joinpath(input_file.stem + new_file_suffix + output_extension)
        )
    else:
        output_file = str(output_path.with_suffix("").with_suffix(output_extension))

    mkvmerge_resort_command = [
        "mkvmerge",
        "--output",
        output_file,
        "(",
        str(input_file),
        ")",
        "--track-order",
        track_order_args,
    ]

    process = ProcessCommand(logger)
    process.run("MKVmerge resort", mkvmerge_resort_command)

    if item_index != total_items - 1:
        return

    logger.info(
        f"MKVmerge resort streams batch `{batch_index}` for `{batch_name}` completed."
    )


def multisort_by_preset(streams: list, preset: dict) -> list:
    """
    Sorts a list of dictionaries in descending order based on the specified keys in the `specs` dictionary.

    Args:
        streams (list): The list of dictionaries to be sorted.
        preset (dict): A dictionary containing the keys and their corresponding sorting order (True for descending,
        False for ascending).

    Returns:
        list: The sorted list of dictionaries.
    """

    for key, reverse in list(preset.items()):
        streams.sort(
            key=lambda nx: nx["properties"][key] if key in nx["properties"] else "",
            reverse=reverse,
        )

    return streams


@logger.catch
@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog="Repository: https://github.com/ToshY/mkvresort",
)
@click.option(
    "--input-path",
    "-i",
    type=click.Path(exists=True, dir_okay=True, file_okay=True, resolve_path=True),
    required=True,
    multiple=True,
    callback=InputPathChecker(),
    help="Path to input file or directory",
)
@click.option(
    "--output-path",
    "-o",
    type=click.Path(dir_okay=True, file_okay=True, resolve_path=True),
    required=True,
    multiple=True,
    callback=OutputPathChecker(),
    help="Path to output file or directory",
)
@click.option(
    "--preset",
    "-p",
    type=click.Path(exists=True, dir_okay=False, file_okay=True, resolve_path=True),
    required=False,
    multiple=True,
    callback=PresetPathChecker(),
    default=["./preset/default.json"],
    show_default=True,
    help="Path to JSON file containing field name and direction for sorting streams",
)
def cli(input_path, output_path, preset):
    combined_result = combine_arguments_by_batch(input_path, output_path, preset)

    # Identify track order
    for item in combined_result:
        current_batch = item.get("batch")
        current_preset = item.get("preset")
        current_input_original_batch_name = item.get("input").get("given")
        current_input_files = item.get("input").get("resolved")
        total_current_input_files = len(current_input_files)

        to_be_resorted_for_batch = []
        for current_file_path_index, current_file_path in enumerate(
            current_input_files
        ):
            mkvmerge_identify_result = mkvmerge_identify_streams(
                current_file_path,
                total_current_input_files,
                current_file_path_index,
                current_batch,
                current_input_original_batch_name,
            )

            to_be_resorted = []
            for stream_info in mkvmerge_identify_result:
                streams_for_type = mkvmerge_identify_result[stream_info]["streams"]
                streams_for_type_ids = [
                    stream_item["id"] for stream_item in streams_for_type
                ]

                sorted_list_by_preset = multisort_by_preset(
                    streams_for_type, current_preset
                )  # noqa

                for current_stream_index, current_stream in enumerate(
                    streams_for_type_ids
                ):
                    found_index = find_in_dict(
                        input_list=sorted_list_by_preset, key="id", value=current_stream
                    )
                    if current_stream_index != found_index:
                        (
                            streams_for_type_ids[current_stream_index],
                            streams_for_type_ids[found_index],
                        ) = (
                            streams_for_type_ids[found_index],
                            streams_for_type_ids[current_stream_index],
                        )

                to_be_resorted = to_be_resorted + streams_for_type_ids

            to_be_resorted_for_batch.append(to_be_resorted)

        item["track_order"] = to_be_resorted_for_batch

    # Resort
    for item in combined_result:
        current_batch = item.get("batch")
        current_track_order = item.get("track_order")
        current_output = item.get("output").get("resolved")
        current_input_original_batch_name = item.get("input").get("given")
        current_input_files = item.get("input").get("resolved")
        total_current_input_files = len(current_input_files)

        for current_file_path_index, current_file_path in enumerate(
            current_input_files
        ):
            mkvmerge_resort_streams(
                current_file_path,
                current_output,
                current_track_order[current_file_path_index],
                total_current_input_files,
                current_file_path_index,
                current_batch,
                current_input_original_batch_name,
            )
