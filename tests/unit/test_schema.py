"""
TODO
"""

from tomlkit import parse

from cppython_core.schema import PyProject


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
        generator = "test_generator"\n
        target = "executable"\n
        install-path = ""\n
        """

        document = parse(data)
        pyproject = PyProject(**document)
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
        assert pyproject.tool.cppython is None
