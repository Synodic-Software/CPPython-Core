"""Tests the plugin schema"""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from cppython_core.plugin_schema.generator import Generator, GeneratorConfiguration
from cppython_core.plugin_schema.provider import Provider, ProviderConfiguration
from cppython_core.plugin_schema.vcs import VersionControl, VersionControlConfiguration
from cppython_core.schema import (
    CPPythonData,
    PluginDataConfiguration,
    ProjectConfiguration,
)


class TestPluginSchema:
    """Test validation"""

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

        data = CPPythonData()

        plugin_attribute = getattr(data, group)
        plugin_attribute[name] = {"heck": "yeah"}

        with mocker.MagicMock() as mock:
            mock.name.return_value = name
            mock.group.return_value = group

            extracted_data = data.extract_plugin_data(mock)

        plugin_attribute = getattr(data, group)
        assert plugin_attribute[name] == extracted_data

    @pytest.mark.parametrize(
        "configuration_type",
        [
            ProviderConfiguration,
            GeneratorConfiguration,
            VersionControlConfiguration,
        ],
    )
    def test_plugin_configuration(self, configuration_type: type[PluginDataConfiguration]) -> None:
        """_summary_

        Args:
            configuration_type: _description_
        """

        config = ProjectConfiguration(pyproject_file=Path("pyproject.toml"), version="0.1.0")
        plugin_config = configuration_type.create(config)

        assert plugin_config
