"""Core Utilities
"""

import json
import logging
import subprocess
from logging import Logger
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from cppython_core.exceptions import ProcessError
from cppython_core.schema import ModelT


def subprocess_call(
    arguments: list[str | Path], logger: Logger, log_level: int = logging.WARNING, suppress: bool = False, **kwargs: Any
) -> None:
    """Executes a subprocess call with logger and utility attachments. Captures STDOUT and STDERR

    Args:
        arguments: Arguments to pass to Popen
        logger: The logger to log the process pipes to
        log_level: The level to log to. Defaults to logging.WARNING.
        suppress: Mutes logging output. Defaults to False.
        kwargs: Keyword arguments to pass to subprocess.Popen

    Raises:
        ProcessError: If the underlying process fails
    """

    with subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, **kwargs) as process:
        if process.stdout is None:
            return

        with process.stdout as pipe:
            for line in iter(pipe.readline, ""):
                if not suppress:
                    logger.log(log_level, line.rstrip())

    if process.returncode != 0:
        raise ProcessError("Subprocess task failed")


def read_model_json(path: Path, model: type[ModelT]) -> ModelT:
    """Reading routine. Only keeps Model data

    Args:
        path: The file to read
        model: The model to read

    Returns:
        The read model
    """

    return model.parse_file(path=path)


def read_json(path: Path) -> Any:
    """Reading routine

    Args:
        path: The json file to read

    Returns:
        The json data
    """

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_model_json(path: Path, model: BaseModel) -> None:
    """Writing routine. Only writes model data

    Args:
        path: The json file to write
        model: The model to write into a json
    """

    serialized = json.loads(model.json(exclude_none=True))
    with open(path, "w", encoding="utf8") as file:
        json.dump(serialized, file, ensure_ascii=False, indent=4)


def write_json(path: Path, data: Any) -> None:
    """Writing routine

    Args:
        path: The json to write
        data: The data to write into json
    """

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
