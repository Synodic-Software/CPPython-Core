"""
Core Utilities
"""
import subprocess
from logging import getLogger
from pathlib import Path

cppython_logger = getLogger("cppython")


def subprocess_call(arguments: list[str | Path], suppress: bool = False, **kwargs):
    """
    Executes a subprocess call with logger and utility attachments. Captures STDOUT and STDERR
    """

    try:
        process = subprocess.run(
            arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True, text=True, **kwargs
        )

        if not suppress:
            cppython_logger.info(process.stdout)

    except subprocess.CalledProcessError as error:

        if not suppress:
            cppython_logger.error(f"The process failed with: {error.stdout}")

        raise error
