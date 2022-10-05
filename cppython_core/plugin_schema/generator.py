"""Generator data plugin definitions"""
from __future__ import annotations

from typing import TypeVar

from pydantic import Field
from pydantic.types import DirectoryPath

from cppython_core.schema import DataPlugin, PluginGroupData


class GeneratorData(PluginGroupData):
    """Base class for the configuration data that is set by the project for the generator"""

    root_directory: DirectoryPath = Field(description="The directory where the pyproject.toml lives")


class Generator(DataPlugin[GeneratorData]):
    """Abstract type to be inherited by CPPython Generator plugins"""

    @staticmethod
    def group() -> str:
        """The plugin group name as used by 'setuptools'summary

        Returns:
            The group name
        """
        return "generator"


GeneratorT = TypeVar("GeneratorT", bound=Generator)
