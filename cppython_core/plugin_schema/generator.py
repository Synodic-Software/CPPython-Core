"""Generator data plugin definitions"""
from typing import Protocol, TypeVar, runtime_checkable

from pydantic import Field
from pydantic.types import DirectoryPath

from cppython_core.schema import DataPlugin, PluginGroupData, SyncData


class GeneratorGroupData(PluginGroupData):
    """Base class for the configuration data that is set by the project for the generator"""

    root_directory: DirectoryPath = Field(description="The directory where the pyproject.toml lives")


@runtime_checkable
class Generator(DataPlugin[GeneratorGroupData], Protocol):
    """Abstract type to be inherited by CPPython Generator plugins"""

    def sync(self, sync_data: SyncData) -> None:
        """Synchronizes generator files and state with the providers input

        Args:
            sync_data: List of information gathered from providers
        """


GeneratorT = TypeVar("GeneratorT", bound=Generator)
