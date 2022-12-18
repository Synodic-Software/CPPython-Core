"""Tests the plugin schema"""

from importlib.metadata import EntryPoint
from typing import LiteralString

from cppython_core.resolution import extract_generator_data, extract_provider_data
from cppython_core.schema import CPPythonLocalConfiguration, DataPlugin, PluginGroupData
from tests.data.mock import MockAbstractPlugin


class TestDataPluginSchema:
    """Test validation"""

    def test_extract_provider_data(self) -> None:
        """Test data extraction for plugin

        Args:
            mock_plugin_type: _description_
        """

        name = "test_provider"
        group = "provider"
        data = CPPythonLocalConfiguration()

        plugin_attribute = getattr(data, group)
        plugin_attribute[name] = {"heck": "yeah"}

        plugin = mock_plugin_type()

        extracted_data = extract_provider_data(data, plugin)

        plugin_attribute = getattr(data, group)
        assert plugin_attribute[name] == extracted_data

    def test_extract_generators_data(self) -> None:
        """Test data extraction for plugins"""

        name = "test_generator"
        group = "generator"
        data = CPPythonLocalConfiguration()

        plugin_attribute = getattr(data, group)
        plugin_attribute[name] = {"heck": "yeah"}

        extracted_data = extract_generator_data(data, mock)

        plugin_attribute = getattr(data, group)
        assert plugin_attribute[name] == extracted_data

    def test_construction(self) -> None:
        """Tests DataPlugin construction"""

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

        plugin = DataPluginImplementation(entry, DataPluginImplementationData(), mock)
        assert plugin
