"""Tests the plugin schema"""

from importlib.metadata import EntryPoint
from typing import LiteralString

from pytest_mock import MockerFixture

from cppython_core.resolution import extract_generator_data, extract_provider_data
from cppython_core.schema import CPPythonLocalConfiguration, DataPlugin, PluginGroupData


class TestDataPluginSchema:
    """Test validation"""

    def test_extract_provider_data(self, mocker: MockerFixture) -> None:
        """Test data extraction for plugins

        Args:
            mocker: Mocking fixture
        """

        name = "test_provider"
        group = "provider"
        data = CPPythonLocalConfiguration()

        plugin_attribute = getattr(data, group)
        plugin_attribute[name] = {"heck": "yeah"}

        with mocker.MagicMock() as mock:
            mock.name = name
            mock.group = group

            extracted_data = extract_provider_data(data, mock)

        plugin_attribute = getattr(data, group)
        assert plugin_attribute[name] == extracted_data

    def test_extract_generators_data(self, mocker: MockerFixture) -> None:
        """Test data extraction for plugins

        Args:
            mocker: Mocking fixture
        """

        name = "test_generator"
        group = "generator"
        data = CPPythonLocalConfiguration()

        plugin_attribute = getattr(data, group)
        plugin_attribute[name] = {"heck": "yeah"}

        with mocker.MagicMock() as mock:
            mock.name = name
            mock.group = group

            extracted_data = extract_generator_data(data, mock)

        plugin_attribute = getattr(data, group)
        assert plugin_attribute[name] == extracted_data

    def test_construction(self, mocker: MockerFixture) -> None:
        """Tests DataPlugin construction

        Args:
            mocker: Mocking fixture
        """

        class DataPluginImplementationData(PluginGroupData):
            """Currently Empty"""

        class DataPluginImplementation(DataPlugin[DataPluginImplementationData]):
            """Currently Empty"""

            @staticmethod
            def cppython_group() -> LiteralString:
                """Mocked function

                Returns:
                    The group name
                """
                return "group"

        entry = EntryPoint(name="test", value="value", group="cppython.group")

        with mocker.MagicMock() as mock:
            plugin = DataPluginImplementation(entry, DataPluginImplementationData(), mock)
            assert plugin
