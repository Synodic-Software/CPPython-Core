"""Generator data plugin definitions"""

from typing import Any, TypeVar

from pydantic import Field
from pydantic.types import DirectoryPath

from cppython_core.schema import (
    DataPlugin,
    PluginData,
    PluginDataConfiguration,
    PluginDataResolved,
)


class GeneratorConfiguration(PluginDataConfiguration):
    """Base class for the configuration data that is set by the project for the generator"""

    root_directory: DirectoryPath = Field(description="The directory where the pyproject.toml lives")


class GeneratorDataResolved(PluginDataResolved):
    """Base class for the configuration data that will be resolved from 'GeneratorData'"""


GeneratorDataResolvedT = TypeVar("GeneratorDataResolvedT", bound=GeneratorDataResolved)


class GeneratorData(PluginData[GeneratorDataResolvedT]):
    """Base class for the configuration data that will be read by the interface and given to the generator"""


GeneratorDataT = TypeVar("GeneratorDataT", bound=GeneratorData[Any])


class Generator(DataPlugin[GeneratorConfiguration, GeneratorDataT, GeneratorDataResolvedT]):
    """Abstract type to be inherited by CPPython Generator plugins"""

    @staticmethod
    def group() -> str:
        """The plugin group name as used by 'setuptools'summary

        Returns:
            The group name
        """
        return "generator"


GeneratorT = TypeVar("GeneratorT", bound=Generator[Any, Any])
