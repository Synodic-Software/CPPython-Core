"""
Tests the scope of utilities
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
    Tests the utility functionality
    """

    def test_root_log(self, caplog: LogCaptureFixture):
        """
        Ensures that the root logger is written to by plugins
        """

        console_logger = StreamHandler()
        cppython_logger.addHandler(console_logger)

        class MockPlugin(Plugin):
            """
            A dummy plugin to verify logging metadata
            """

            @staticmethod
            def name() -> str:
                """
                Static name to compare in this test
                """
                return "mock"

            @staticmethod
            def group() -> str:
                """
                Static group to compare in this test
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
        Test subprocess_call suppression flag
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
