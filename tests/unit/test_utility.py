"""Tests the scope of utilities
"""

import logging
from logging import StreamHandler
from pathlib import Path
from sys import executable

import pytest
from pytest import LogCaptureFixture

from cppython_core.exceptions import ProcessError
from cppython_core.schema import Plugin
from cppython_core.utility import subprocess_call

cppython_logger = logging.getLogger("cppython")
cppython_logger.addHandler(StreamHandler())


class TestUtility:
    """Tests the utility functionality"""

    def test_plugin_log(self, caplog: LogCaptureFixture) -> None:
        """Ensures that the root logger receives the auto-gathered plugin logger

        Args:
            caplog: Fixture for capturing logging input
        """

        class MockPlugin(Plugin):
            """A dummy plugin to verify logging metadata"""

            @staticmethod
            def name() -> str:
                """Static name to compare in this test

                Returns:
                    Name of the plugin
                """
                return "mock"

            @staticmethod
            def group() -> str:
                """Static group to compare in this test

                Returns:
                    Name of the group
                """
                return "group"

        logger = MockPlugin.logger()

        with caplog.at_level(logging.INFO):
            logger.info("test")
            assert caplog.record_tuples == [("cppython.group.mock", logging.INFO, "test")]

    def test_subprocess_stdout(self, caplog: LogCaptureFixture) -> None:
        """Test subprocess_call

        Args:
            caplog: Fixture for capturing logging input
        """

        python = Path(executable)

        with caplog.at_level(logging.INFO):
            subprocess_call([python, "-c", "import sys; print('Test Out', file = sys.stdout)"], cppython_logger)

        assert len(caplog.records) == 1
        assert "Test Out" == caplog.records[0].message

    def test_subprocess_stderr(self, caplog: LogCaptureFixture) -> None:
        """Test subprocess_call

        Args:
            caplog: Fixture for capturing logging input
        """

        python = Path(executable)

        with caplog.at_level(logging.INFO):
            subprocess_call([python, "-c", "import sys; print('Test Error', file = sys.stderr)"], cppython_logger)

        assert len(caplog.records) == 1
        assert "Test Error" == caplog.records[0].message

    def test_subprocess_suppression(self, caplog: LogCaptureFixture) -> None:
        """Test subprocess_call suppression flag

        Args:
            caplog: Fixture for capturing logging input
        """

        python = Path(executable)

        with caplog.at_level(logging.INFO):
            subprocess_call(
                [python, "-c", "import sys; print('Test Out', file = sys.stdout)"], cppython_logger, suppress=True
            )
            assert len(caplog.records) == 0

    def test_subprocess_exit(self, caplog: LogCaptureFixture) -> None:
        """Test subprocess_call exception output

        Args:
            caplog: Fixture for capturing logging input
        """

        python = Path(executable)

        with pytest.raises(ProcessError) as exec_info, caplog.at_level(logging.INFO):
            subprocess_call([python, "-c", "import sys; sys.exit('Test Exit Output')"], cppython_logger)

            assert len(caplog.records) == 1
            assert "Test Exit Output" == caplog.records[0].message

        assert "Subprocess task failed" in str(exec_info.value)

    def test_subprocess_exception(self, caplog: LogCaptureFixture) -> None:
        """Test subprocess_call exception output

        Args:
            caplog: Fixture for capturing logging input
        """

        python = Path(executable)

        with pytest.raises(ProcessError) as exec_info, caplog.at_level(logging.INFO):
            subprocess_call([python, "-c", "import sys; raise Exception('Test Exception Output')"], cppython_logger)
            assert len(caplog.records) == 1
            assert "Test Exception Output" == caplog.records[0].message

        assert "Subprocess task failed" in str(exec_info.value)

    def test_stderr_exception(self, caplog: LogCaptureFixture) -> None:
        """Verify print and exit

        Args:
            caplog: Fixture for capturing logging input
        """
        python = Path(executable)
        with pytest.raises(ProcessError) as exec_info, caplog.at_level(logging.INFO):
            subprocess_call(
                [python, "-c", "import sys; print('Test Out', file = sys.stdout); sys.exit('Test Exit Out')"],
                cppython_logger,
            )
            assert len(caplog.records) == 2
            assert "Test Out" == caplog.records[0].message
            assert "Test Exit Out" == caplog.records[1].message

        assert "Subprocess task failed" in str(exec_info.value)

    def test_stdout_exception(self, caplog: LogCaptureFixture) -> None:
        """Verify print and exit

        Args:
            caplog: Fixture for capturing logging input
        """
        python = Path(executable)
        with pytest.raises(ProcessError) as exec_info, caplog.at_level(logging.INFO):
            subprocess_call(
                [python, "-c", "import sys; print('Test Error', file = sys.stderr); sys.exit('Test Exit Error')"],
                cppython_logger,
            )
            assert len(caplog.records) == 2
            assert "Test Error" == caplog.records[0].message
            assert "Test Exit Error" == caplog.records[1].message

        assert "Subprocess task failed" in str(exec_info.value)
