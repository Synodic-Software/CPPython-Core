"""Test data resolution
"""

from pathlib import Path

from pytest_mock import MockerFixture

from cppython_core.resolution import (
    resolve_cppython,
    resolve_cppython_plugin,
    resolve_generator,
    resolve_pep621,
    resolve_project_configuration,
    resolve_provider,
)
from cppython_core.schema import (
    CPPythonGlobalConfiguration,
    CPPythonLocalConfiguration,
    PEP621Configuration,
    ProjectConfiguration,
    ProjectData,
)


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
        local_config = CPPythonLocalConfiguration(**{"install-path": tmp_path})
        global_config = CPPythonGlobalConfiguration()

        project_config = ProjectData(pyproject_file=pyproject)

        # Function to test
        resolved = resolve_cppython(local_config, global_config, project_config)

        # Test that paths are created successfully
        assert resolved.build_path.exists()
        assert resolved.tool_path.exists()
        assert resolved.install_path.exists()

        # Ensure that all values are populated
        class_variables = vars(resolved)

        assert len(class_variables)
        assert not None in class_variables.values()

    def test_cppython_plugin_resolve(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test the CPPython plugin schema resolve function

        Args:
            tmp_path: Temporary path with a lifetime of this test function
            mocker: Mocker fixture
        """

        # Create a working configuration
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("")

        # Data definition
        local_config = CPPythonLocalConfiguration(**{"install-path": tmp_path})
        global_config = CPPythonGlobalConfiguration()

        project_config = ProjectData(pyproject_file=pyproject)

        resolved = resolve_cppython(local_config, global_config, project_config)

        with mocker.MagicMock() as plugin_type:
            plugin_type.name.return_value = "mock"
            assert resolve_cppython_plugin(resolved, plugin_type)

    def test_pep621_resolve(self) -> None:
        """Test the PEP621 schema resolve function"""

        data = PEP621Configuration(name="pep621-resolve-test", dynamic=["version"])
        config = ProjectConfiguration(pyproject_file=Path("pyproject.toml"), version="0.1.0")
        resolved = resolve_pep621(data, config)

        class_variables = vars(resolved)

        assert len(class_variables)
        assert not None in class_variables.values()

    def test_project_resolve(self) -> None:
        """Tests project configuration resolution"""

        config = ProjectConfiguration(pyproject_file=Path("pyproject.toml"), version="0.1.0")
        assert resolve_project_configuration(config)

    def test_generator_resolve(self) -> None:
        """Tests generator resolution"""

        project_data = ProjectData(pyproject_file=Path("pyproject.toml"))
        assert resolve_generator(project_data)

    def test_provider_resolve(self) -> None:
        """Tests provider resolution"""

        project_data = ProjectData(pyproject_file=Path("pyproject.toml"))
        assert resolve_provider(project_data)
