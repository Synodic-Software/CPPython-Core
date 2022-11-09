"""Tests the plugin schema"""

from importlib.metadata import EntryPoint
import pytest
from pytest_mock import MockerFixture

from cppython_core.schema import CPPythonLocalConfiguration, DataPlugin, PluginGroupData


class TestDataPluginSchema:
    """Test validation"""

    @pytest.mark.parametrize(
        "name, group",
        [
            ("test_provider", "provider"),
            ("test_generator", "generator"),
        ],
    )
    def test_extract_plugin_data(self, mocker: MockerFixture, name: str, group: str) -> None:
        """Test data extraction for plugins

        Args:
            mocker: Mocking fixture
            name: The plugin name
            group: The plugin group
        """

        data = CPPythonLocalConfiguration()

        plugin_attribute = getattr(data, group)
        plugin_attribute[name] = {"heck": "yeah"}

        with mocker.MagicMock() as mock:
            mock.name = name
            mock.group = group

            extracted_data = data.extract_plugin_data(mock)

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

        entry = EntryPoint(name="test", value="value", group="cppython.group")

        with mocker.MagicMock() as mock:
            plugin = DataPluginImplementation(entry, DataPluginImplementationData(), mock)
            assert plugin
