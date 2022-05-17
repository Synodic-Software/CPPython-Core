"""
Core Utilities
"""
import subprocess
from logging import getLogger
from pathlib import Path

cppython_logger = getLogger("cppython")


def subprocess_call(arguments: list[str | Path]):
    """
    Executes a subprocess call with logger and utility attachments. Captures STDOUT and STDERR
    """

    try:
        process = subprocess.run(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True, text=True)
        cppython_logger.info(process.stdout)
    except subprocess.CalledProcessError as error:
        cppython_logger.error(f"The process failed with: {error.stdout}")
