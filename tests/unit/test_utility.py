"""
TODO
"""

import logging
import subprocess
from logging import StreamHandler
from pathlib import Path
from sys import executable

import pytest
from pytest import LogCaptureFixture

from cppython_core.schema import Plugin
from cppython_core.utility import cppython_logger, subprocess_call


class TestUtility:
    """
    TODO
    """

    def test_root_log(self, caplog: LogCaptureFixture):
        """
        TODO
        """

        console_logger = StreamHandler()
        cppython_logger.addHandler(console_logger)

        class MockPlugin(Plugin):
            """
            TODO
            """

            @staticmethod
            def name() -> str:
                """
                TODO
                """
                return "mock"

            @staticmethod
            def group() -> str:
                """
                TODO
                """
                return "group"

        logger = MockPlugin.logger
        logger.info("test")

        with caplog.at_level(logging.INFO):
            logger.info("test")
            assert caplog.records[0].message == "test"

    def test_subprocess_output(self, caplog: LogCaptureFixture):
        """
        Test subprocess_call
        """

        console_logger = StreamHandler()
        cppython_logger.addHandler(console_logger)

        python = Path(executable)

        with caplog.at_level(logging.INFO):
            subprocess_call([python, "-c", "import sys; print('Test Out', file = sys.stdout)"])
            assert "Test Out" in caplog.text

        with caplog.at_level(logging.INFO):
            subprocess_call([python, "-c", "import sys; print('Test Error', file = sys.stderr)"])
            assert "Test Error" in caplog.text

    def test_subprocess_suppression(self, caplog: LogCaptureFixture):
        """
        Test subprocess_call supression flag
        """

        console_logger = StreamHandler()
        cppython_logger.addHandler(console_logger)

        python = Path(executable)

        with caplog.at_level(logging.INFO):
            subprocess_call([python, "-c", "import sys; print('Test Out', file = sys.stdout)"], suppress=True)
            assert len(caplog.text) == 0

    def test_subprocess_exception(self):
        """
        Test subprocess_call exception output
        """

        python = Path(executable)

        with pytest.raises(subprocess.CalledProcessError):
            subprocess_call([python, "-c", "import sys; sys.exit('My error message')"])
