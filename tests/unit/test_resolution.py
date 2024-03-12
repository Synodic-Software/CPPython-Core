"""Test data resolution"""

from pathlib import Path

import pytest
from pydantic import Field
from synodic_utilities.utility import TypeName

from cppython_core.exceptions import ConfigException
from cppython_core.resolution import (
    PluginCPPythonData,
    resolve_cppython,
    resolve_model,
    resolve_pep621,
    resolve_project_configuration,
)
from cppython_core.schema import (
    CPPythonGlobalConfiguration,
    CPPythonLocalConfiguration,
    CPPythonModel,
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

        plugin_build_data = PluginCPPythonData(
            generator_name=TypeName("generator"), provider_name=TypeName("provider"), scm_name=TypeName("scm")
        )

        assert resolve_cppython(
            cppython_local_configuration, cppython_global_configuration, project_data, plugin_build_data
        )

    def test_model_resolve(self) -> None:
        """Test model resolution"""

        class MockModel(CPPythonModel):
            """Mock model for testing"""

            field: str = Field()

        bad_data = {"field": 4}

        with pytest.raises(ConfigException) as error:
            resolve_model(MockModel, bad_data)

        assert error.value.error_count == 1

        good_data = {"field": "good"}

        resolve_model(MockModel, good_data)
