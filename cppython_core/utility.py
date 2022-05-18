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
        process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, **kwargs)

        if not suppress:
            with process.stdout as pipe:
                for line in iter(pipe.readline, ""):
                    cppython_logger.info(line.rstrip())

        exitcode = process.wait()

        if exitcode != 0:
            raise subprocess.CalledProcessError(exitcode, arguments)

    except subprocess.CalledProcessError as error:

        if not suppress:
            cppython_logger.error(f"The process failed with: {error.stdout}")

        raise error
