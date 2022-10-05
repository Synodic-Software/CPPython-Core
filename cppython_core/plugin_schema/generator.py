"""Generator data plugin definitions"""
from __future__ import annotations

from typing import TypeVar

from pydantic import Field
from pydantic.types import DirectoryPath

from cppython_core.schema import DataPlugin, PluginDataConfiguration, ProjectData


class GeneratorConfiguration(PluginDataConfiguration):
    """Base class for the configuration data that is set by the project for the generator"""

    root_directory: DirectoryPath = Field(description="The directory where the pyproject.toml lives")

    @classmethod
    def create(cls, project_data: ProjectData) -> GeneratorConfiguration:
        """Creates an instance from the given project

        Args:
            project_data: The input project configuration

        Returns:
            The plugin specific configuration
        """
        configuration = GeneratorConfiguration(root_directory=project_data.pyproject_file.parent)
        return configuration


class Generator(DataPlugin[GeneratorConfiguration]):
    """Abstract type to be inherited by CPPython Generator plugins"""

    @staticmethod
    def group() -> str:
        """The plugin group name as used by 'setuptools'summary

        Returns:
            The group name
        """
        return "generator"


GeneratorT = TypeVar("GeneratorT", bound=Generator)
