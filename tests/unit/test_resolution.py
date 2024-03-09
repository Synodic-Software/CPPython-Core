"""Test data resolution"""

from pathlib import Path

from synodic_utilities.utility import TypeName

from cppython_core.resolution import (
    PluginBuildData,
    resolve_cppython,
    resolve_pep621,
    resolve_project_configuration,
)
from cppython_core.schema import (
    CPPythonGlobalConfiguration,
    CPPythonLocalConfiguration,
    PEP621Configuration,
    ProjectConfiguration,
)


class TestSchema:
    """Test validation"""

    def test_pep621_resolve(self) -> None:
        """Test the PEP621 schema resolve function"""

        data = PEP621Configuration(name="pep621-resolve-test", dynamic=["version"])
        config = ProjectConfiguration(pyproject_file=Path("pyproject.toml"), version="0.1.0")
        resolved = resolve_pep621(data, config, None)

        class_variables = vars(resolved)

        assert len(class_variables)
        assert not None in class_variables.values()

    def test_project_resolve(self) -> None:
        """Tests project configuration resolution"""

        config = ProjectConfiguration(pyproject_file=Path("pyproject.toml"), version="0.1.0")
        assert resolve_project_configuration(config)

    def test_cppython_resolve(self) -> None:
        """Tests cppython configuration resolution"""

        cppython_local_configuration = CPPythonLocalConfiguration()
        cppython_global_configuration = CPPythonGlobalConfiguration()

        config = ProjectConfiguration(pyproject_file=Path("pyproject.toml"), version="0.1.0")
        project_data = resolve_project_configuration(config)

        plugin_build_data = PluginBuildData(
            generator_name=TypeName("generator"), provider_name=TypeName("provider"), scm_name=TypeName("scm")
        )

        assert resolve_cppython(
            cppython_local_configuration, cppython_global_configuration, project_data, plugin_build_data
        )
