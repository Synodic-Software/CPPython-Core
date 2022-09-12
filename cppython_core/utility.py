"""
Core Utilities
"""

import logging
import subprocess
from logging import Logger
from pathlib import Path
from typing import Any

from cppython_core.exceptions import ProcessError


def subprocess_call(
    arguments: list[str | Path], logger: Logger, log_level: int = logging.WARNING, suppress: bool = False, **kwargs: Any
) -> None:
    """
    Executes a subprocess call with logger and utility attachments. Captures STDOUT and STDERR
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
