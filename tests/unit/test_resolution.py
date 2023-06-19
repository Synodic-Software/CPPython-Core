"""Test data resolution
"""

from pathlib import Path

from cppython_core.resolution import resolve_pep621, resolve_project_configuration
from cppython_core.schema import PEP621Configuration, ProjectConfiguration


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
