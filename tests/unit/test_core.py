"""
TODO
"""

import logging
from logging import StreamHandler

from cppython_core.core import cppython_logger
from cppython_core.schema import Plugin


class TestSchema:
    """
    TODO
    """

    def test_root_log(self, caplog):
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
