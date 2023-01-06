"""Tests the scope of utilities
"""

import logging
from importlib.metadata import EntryPoint
from logging import StreamHandler
from pathlib import Path
from sys import executable

import pytest
from pytest import LogCaptureFixture

from cppython_core.exceptions import ProcessError
from cppython_core.schema import CPPythonModel, Plugin
from cppython_core.utility import canonicalize_name, subprocess_call

cppython_logger = logging.getLogger("cppython")
cppython_logger.addHandler(StreamHandler())


class TestUtility:
    """Tests the utility functionality"""

    class ModelTest(CPPythonModel):
        """Model definition to help test IO utilities"""

        test_path: Path
        test_int: int

    def test_plugin_log(self, caplog: LogCaptureFixture) -> None:
        """Ensures that the root logger receives the auto-gathered plugin logger

        Args:
            caplog: Fixture for capturing logging input
        """

        class MockPlugin(Plugin):
            """A dummy plugin to verify logging metadata"""

        entry = EntryPoint(name="mock", value="value", group="cppython.plugin")
        plugin = MockPlugin(entry)
        logger = plugin.logger

        with caplog.at_level(logging.INFO):
            logger.info("test")
            assert caplog.record_tuples == [("cppython.plugin.mock", logging.INFO, "test")]

    def test_name_normalization(self) -> None:
        """Test that canonicalization works"""

        test = canonicalize_name("BasicPlugin")

        assert test.group == "plugin"
        assert test.name == "basic"

        test = canonicalize_name("AcronymYA")

        assert test.group == "ya"
        assert test.name == "acronym"

        test = canonicalize_name("YAAcronym")
        assert test.group == "acronym"
        assert test.name == "ya"


class TestSubprocess:
    """Subprocess testing"""

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
