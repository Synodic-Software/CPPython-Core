"""Test data resolution
"""

from pathlib import Path
from typing import Any

from cppython_core.resolution import (
    resolve_generator,
    resolve_pep621,
    resolve_project_configuration,
    resolve_provider,
)
from cppython_core.schema import PEP621Configuration, ProjectConfiguration, ProjectData


class TestSchema:
    """Test validation"""

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

    def test_provider_resolve(
        self,
        tmp_path: Path,
    ) -> None:
        """Tests provider resolution

        Args:
            tmp_path: Mocker fixture
        """

        # Create a working configuration
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("")

        project_data = ProjectData(pyproject_file=Path("pyproject.toml"))
        assert resolve_provider(project_data)
