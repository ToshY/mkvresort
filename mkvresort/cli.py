import click
from mkvresort.process import ProcessDisplay
from loguru import logger  # noqa
import json
from pathlib import Path
from mkvresort.banner import cli_banner
from mkvresort.helper import (
    files_in_dir,
    find_in_dict,
    read_json,
    split_list_of_dicts_by_key,
    combine_batches,
)
from rich import print


class InputPathChecker:
    def __call__(self, ctx, param, value):
        if value is None:
            raise click.BadParameter("No path provided")

        results = []
        for batch_number, path in enumerate(value):
            current_batch = {"batch": batch_number + 1}
            p = Path(path)
            if p.exists():
                if p.is_file():
                    current_batch = {
                        **current_batch,
                        "input": {"given": path, "resolved": [p]},
                    }
                elif p.is_dir():
                    files = files_in_dir(p)
                    amount_of_files_in_directory = len(files)
                    if amount_of_files_in_directory == 0:
                        raise click.BadParameter("No files found in directory")

                    current_batch = {
                        **current_batch,
                        "input": {"given": path, "resolved": files},
                    }
                else:
                    raise click.BadParameter("Not a file or directory")
            else:
                raise click.BadParameter("Path does not exist")
            results.append(current_batch)

        return results


class OutputPathChecker:
    def __call__(self, ctx, param, value):
        if value is None:
            raise click.BadParameter("No path provided")

        amount_of_current_param_values = len(value)
        amount_of_input_values = len(ctx.params.get("input_path"))

        if amount_of_input_values != amount_of_current_param_values:
            raise click.BadParameter(
                f"The amount of input values ({amount_of_input_values}) does not "
                f"equal amount of output values ({amount_of_current_param_values})."
            )

        results = []
        for batch_number, path in enumerate(value):
            current_batch = {"batch": batch_number + 1}
            p = Path(path)
            if p.suffix:
                if not p.parent.is_dir():
                    raise FileNotFoundError(
                        f"The parent directory `{str(p.parent)}` "
                        f"for output argument `{str(p)}` does not exist."
                    )
                else:
                    current_batch = {
                        **current_batch,
                        "output": {"given": path, "resolved": p},
                    }
            else:
                if not p.is_dir():
                    p.mkdir()
                current_batch = {
                    **current_batch,
                    "output": {"given": path, "resolved": p},
                }
            results.append(current_batch)

        return results


class SortPathChecker:
    def __call__(self, ctx, param, value: tuple):
        if value is None:
            raise click.BadParameter("No path provided")

        amount_of_current_param_values = len(value)
        amount_of_input_values = len(ctx.params.get("input_path"))

        # Either give 1 value or same exact amount as input values.
        if (
            amount_of_input_values != amount_of_current_param_values
            and amount_of_current_param_values != 1
        ):
            raise click.BadParameter(
                f"The amount of input values ({amount_of_input_values}) does not "
                f"equal amount of sort values ({amount_of_current_param_values})."
            )

        to_be_enumerated = value
        if amount_of_input_values != amount_of_current_param_values:
            to_be_enumerated = value * amount_of_input_values

        results = []
        for batch_number, path in enumerate(to_be_enumerated):
            current_batch: dict = {"batch": batch_number + 1}
            p = Path(path)
            if p.exists():
                if p.is_file():
                    current_batch = {**current_batch, "preset": read_json(p)}
                else:
                    raise click.BadParameter("Not a file")
            else:
                raise click.BadParameter("Path does not exist")
            results.append(current_batch)

        return results


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
        print(
            f"\r\n\r\n> MKVmerge identify batch [cyan]{batch_index}[/cyan] for [cyan]{batch_name}[/cyan] started"
        )

    mkvmerge_identify_command = [
        "mkvmerge",
        "--identify",
        "--identification-format",
        "json",
        str(input_file),
    ]

    process = ProcessDisplay(logger)
    result = process.run("MKVmerge identify", mkvmerge_identify_command)

    # Json output
    mkvidentify_out = json.loads(result.stdout)
    if mkvidentify_out["errors"]:
        raise Exception(
            'MKVidentify encountered the following error: "{}"'.format(
                mkvidentify_out["errors"][0]
            )
        )

    # Split by codec_type
    split_streams, split_keys = split_list_of_dicts_by_key(
        mkvidentify_out["tracks"], "type"
    )

    # Rebuild streams & count per codec type
    streams = {k: {"streams": {}, "count": 0} for k in split_keys}
    for x, s in enumerate(split_keys):
        streams[s]["streams"] = split_streams[x]
        streams[s]["count"] = len(streams[s]["streams"])

    # Sort streams to video - audio - subtitles
    streams = {k: streams[k] for k in ["video", "audio", "subtitles"]}

    if item_index == total_items - 1:
        print(
            f"\r\n> MKVmerge identify batch [cyan]{batch_index}[/cyan] for [cyan]{batch_name}[/cyan] completed"
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
        print(
            f"\r\n\r\n> MKVmerge resort streams batch [cyan]{batch_index}[/cyan] for [cyan]{batch_name}[/cyan] started"
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

    process = ProcessDisplay(logger)
    process.run("MKVmerge resort", mkvmerge_resort_command)

    if item_index == total_items - 1:
        print(
            f"\r\n\r\n> MKVmerge resort streams batch [cyan]{batch_index}[/cyan] for [cyan]{batch_name}[/cyan] "
            f"completed"
        )

    return None


def multisort_by_preset(xs: list, specs: dict) -> list:
    """
    Sorts a list of dictionaries in descending order based on the specified keys in the `specs` dictionary.

    Args:
        xs (list): The list of dictionaries to be sorted.
        specs (dict): A dictionary containing the keys and their corresponding sorting order (True for descending,
        False for ascending).

    Returns:
        list: The sorted list of dictionaries.
    """

    for key, reverse in reversed(list(specs.items())):
        xs.sort(
            key=lambda nx: nx["properties"][key] if key in nx["properties"] else "",
            reverse=reverse,
        )

    return xs


@logger.catch
@click.command(context_settings={"help_option_names": ["-h", "--help"]})
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
    help="Path to output directory",
)
@click.option(
    "--sort",
    "-s",
    type=click.Path(exists=True, dir_okay=False, file_okay=True, resolve_path=True),
    required=False,
    multiple=True,
    callback=SortPathChecker(),
    default=["./preset/default.json"],
    help="Sorting tags",
)
def main(input_path, output_path, sort):
    combined_result = combine_batches(input_path, output_path, sort)

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
            if not current_file_path.exists():
                print(f"File not found: {current_file_path}")
                continue

            probe_result = mkvmerge_identify_streams(
                current_file_path,
                total_current_input_files,
                current_file_path_index,
                current_batch,
                current_input_original_batch_name,
            )

            to_be_resorted = []
            for stream_info in probe_result:
                streams_for_type = probe_result[stream_info]["streams"]
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


def cli():
    """
    A tool for resorting streams.

    Documentation: https://github.com/ToshY/mkvresort
    """

    cli_banner("mkvresort")

    # Stop execution at keyboard input
    try:
        main()
    except KeyboardInterrupt:
        print("\r\n\r\n> [red]Execution cancelled by user[/red]")
        exit()
