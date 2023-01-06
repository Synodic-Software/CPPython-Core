"""Tests the plugin schema"""

from pytest_mock import MockerFixture

from cppython_core.plugin_schema.generator import Generator
from cppython_core.plugin_schema.provider import Provider
from cppython_core.resolution import extract_generator_data, extract_provider_data
from cppython_core.schema import CPPythonLocalConfiguration


class TestDataPluginSchema:
    """Test validation"""

    def test_extract_provider_data(self, mocker: MockerFixture) -> None:
        """Test data extraction for plugin

        Args:
            mocker: Mocker fixture
        """

        name = "test_provider"
        group = "provider"
        data = CPPythonLocalConfiguration()

        plugin_attribute = getattr(data, group)
        plugin_attribute[name] = {"heck": "yeah"}

        plugin = mocker.create_autospec(Provider)
        plugin.name.return_value = "test_provider"

        extracted_data = extract_provider_data(data, plugin)

        plugin_attribute = getattr(data, group)
        assert plugin_attribute[name] == extracted_data

    def test_extract_generators_data(self, mocker: MockerFixture) -> None:
        """Test data extraction for plugins

        Args:
            mocker: Mocker fixture
        """

        name = "test_generator"
        group = "generator"
        data = CPPythonLocalConfiguration()

        plugin_attribute = getattr(data, group)
        plugin_attribute[name] = {"heck": "yeah"}

        plugin = mocker.create_autospec(Generator)
        plugin.name.return_value = "test_generator"

        extracted_data = extract_generator_data(data, plugin)

        plugin_attribute = getattr(data, group)
        assert plugin_attribute[name] == extracted_data
