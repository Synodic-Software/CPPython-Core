"""Tests the plugin schema"""

import pytest
from packaging.utils import canonicalize_name
from pytest_mock import MockerFixture

from cppython_core.plugin_schema.generator import Generator
from cppython_core.plugin_schema.provider import Provider
from cppython_core.plugin_schema.vcs import VersionControl
from cppython_core.schema import CPPythonLocalConfiguration, Plugin


class TestPluginSchema:
    """Test validation"""

    plugin_types = [Provider, Generator, VersionControl]

    @pytest.mark.parametrize(
        "name, group",
        [
            ("test_provider", Provider.group()),
            ("test_generator", Generator.group()),
            ("test_vcs", VersionControl.group()),
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
            mock.name.return_value = name
            mock.group.return_value = group

            extracted_data = data.extract_plugin_data(mock)

        plugin_attribute = getattr(data, group)
        assert plugin_attribute[name] == extracted_data

    @pytest.mark.parametrize(
        "plugin_type",
        plugin_types,
    )
    def test_group(self, plugin_type: Plugin) -> None:
        """Validates the group name

        Args:
            plugin_type: The input plugin type
        """

        assert plugin_type.group() == canonicalize_name(plugin_type.group())
