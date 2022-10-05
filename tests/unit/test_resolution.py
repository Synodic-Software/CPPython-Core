"""Test data resolution
"""

from pathlib import Path

from cppython_core.plugin_schema.generator import GeneratorData
from cppython_core.plugin_schema.provider import ProviderData
from cppython_core.plugin_schema.vcs import VersionControlData
from cppython_core.schema import PEP621, CPPythonData, PluginGroupData, ProjectData


class TestSchema:
    """Test validation"""

    def test_cppython_resolve(self, tmp_path: Path) -> None:
        """Test the CPPython schema resolve function

        Args:
            tmp_path: Temporary path with a lifetime of this test function
        """

        # Create a working configuration
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("")

        # Data definition
        data = CPPythonData()
        data.install_path = tmp_path

        config = ProjectData(pyproject_file=pyproject, version="0.1.0")

        # Function to test
        resolved = data.resolve(config)

        # Test that paths are created successfully
        assert resolved.build_path.exists()
        assert resolved.tool_path.exists()
        assert resolved.install_path.exists()

        # Ensure that all values are populated
        class_variables = vars(resolved)

        assert len(class_variables)
        assert not None in class_variables.values()

    def test_pep621_resolve(self) -> None:
        """Test the PEP621 schema resolve function"""

        data = PEP621(name="pep621-resolve-test", dynamic=["version"])
        config = ProjectData(pyproject_file=Path("pyproject.toml"), version="0.1.0")
        resolved = data.resolve(config)

        class_variables = vars(resolved)

        assert len(class_variables)
        assert not None in class_variables.values()

    @pytest.mark.parametrize(
        "configuration_type",
        [
            ProviderData,
            GeneratorData,
            VersionControlData,
        ],
    )
    def test_plugin_configuration(self, configuration_type: type[PluginGroupData]) -> None:
        """_summary_

        Args:
            configuration_type: _description_
        """

        config = ProjectData(pyproject_file=Path("pyproject.toml"), version="0.1.0")
        plugin_config = configuration_type.create(config)

        assert plugin_config
