import click
from pathlib import Path
from mkvresort.helper import (
    files_in_dir,
    read_json,
)


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


class PresetPathChecker:
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
                f"equal amount of preset values ({amount_of_current_param_values})."
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
                    current_batch = {**current_batch, param.name: read_json(p)}
                else:
                    raise click.BadParameter("Not a file")
            else:
                raise click.BadParameter("Path does not exist")
            results.append(current_batch)

        return results
