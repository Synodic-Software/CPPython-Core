"""Test custom schema validation that cannot be verified by the Pydantic validation
"""

from pathlib import Path

import pytest
from tomlkit import parse

from cppython_core.schema import (
    PEP508,
    PEP621,
    CPPythonData,
    CPPythonDataResolved,
    ProjectConfiguration,
    PyProject,
)


class TestSchema:
    """Test validation"""

    def test_cppython_data(self) -> None:
        """Ensures that the CPPython config data can be defaulted"""
        CPPythonData()

    def test_cppython_table(self) -> None:
        """Ensures that the nesting yaml table behavior can be read properly"""

        data = """
        [project]\n
        name = "test"\n
        version = "1.0.0"\n
        description = "A test document"\n

        [tool.cppython]\n
        target = "executable"\n
        """

        document = parse(data).value
        pyproject = PyProject(**document)
        assert pyproject.tool is not None
        assert pyproject.tool.cppython is not None

    def test_empty_cppython(self) -> None:
        """Ensure that the common none condition works"""

        data = """
        [project]\n
        name = "test"\n
        version = "1.0.0"\n
        description = "A test document"\n

        [tool.test]\n
        """

        document = parse(data).value
        pyproject = PyProject(**document)
        assert pyproject.tool is not None
        assert pyproject.tool.cppython is None

    def test_508(self) -> None:
        """Ensure correct parsing of the 'packaging' type via the PEP508 intermediate type"""

        requirement = PEP508('requests [security,tests] >= 2.8.1, == 2.8.* ; python_version < "2.7"')

        assert requirement.name == "requests"

        with pytest.raises(ValueError):
            PEP508("this is not conforming")

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

        config = ProjectConfiguration(pyproject_file=pyproject, version="0.1.0")

        # Function to test
        resolved = data.resolve(CPPythonDataResolved, config)

        # Test that paths are created successfully
        assert resolved.build_path.exists()
        assert resolved.tool_path.exists()
        assert resolved.install_path.exists()

        # Ensure that all values are populated
        class_variables = vars(resolved)

        assert len(class_variables)
        assert not None in class_variables.values()

    def test_pep621_version(self) -> None:
        """Tests the dynamic version resolution"""

        with pytest.raises(ValueError):
            PEP621(name="empty-test")

        with pytest.raises(ValueError):
            PEP621(name="both-test", version="1.0.0", dynamic=["version"])

    def test_pep621_resolve(self) -> None:
        """Test the PEP621 schema resolve function"""

        data = PEP621(name="pep621-resolve-test", dynamic=["version"])
        config = ProjectConfiguration(pyproject_file=Path("pyproject.toml"), version="0.1.0")
        resolved = data.resolve(config)

        class_variables = vars(resolved)

        assert len(class_variables)
        assert not None in class_variables.values()
