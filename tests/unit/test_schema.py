"""
TODO
"""

from _pytest.python_api import raises
from pytest import raises
from tomlkit import parse

from cppython_core.schema import PEP508, CPPythonData, PyProject, TargetEnum


class TestSchema:
    """
    TODO
    """

    def test_cppython_table(self):
        """
        TODO
        """

        data = """
        [project]\n
        name = "test"\n
        version = "1.0.0"\n
        description = "A test document"\n

        [tool.cppython]\n
        target = "executable"\n
        """

        document = parse(data)
        pyproject = PyProject(**document)
        assert pyproject.tool is not None
        assert pyproject.tool.cppython is not None

    def test_empty_cppython(self):
        """
        TODO
        """

        data = """
        [project]\n
        name = "test"\n
        version = "1.0.0"\n
        description = "A test document"\n

        [tool.test]\n
        """

        document = parse(data)
        pyproject = PyProject(**document)
        assert pyproject.tool is not None
        assert pyproject.tool.cppython is None

    def test_508(self):
        """
        TODO
        """

        requirement = PEP508('requests [security,tests] >= 2.8.1, == 2.8.* ; python_version < "2.7"')

        assert requirement.name == "requests"

        with raises(ValueError):
            PEP508("this is not conforming")

    def test_cppython_data(self):
        """
        TODO
        """
        CPPythonData(target=TargetEnum.EXE)
