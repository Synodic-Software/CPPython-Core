"""
Core Utilities
"""
import logging
import subprocess
from pathlib import Path
from typing import Any

cppython_logger = logging.getLogger("cppython")


def subprocess_call(
    arguments: list[str | Path], log_level: int = logging.WARNING, suppress: bool = False, **kwargs: Any
):
    """
    Executes a subprocess call with logger and utility attachments. Captures STDOUT and STDERR
    """

    try:
        process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, **kwargs)

        if not suppress:
            assert process.stdout is not None
            with process.stdout as pipe:
                for line in iter(pipe.readline, ""):
                    cppython_logger.log(log_level, line.rstrip())

        exitcode = process.wait()

        if exitcode != 0:
            raise subprocess.CalledProcessError(exitcode, arguments)

    except subprocess.CalledProcessError as error:

        if not suppress:
            cppython_logger.error(f"The process failed with: {error.stdout}")

        raise error
