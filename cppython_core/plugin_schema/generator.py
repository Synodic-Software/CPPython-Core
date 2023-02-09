"""Generator data plugin definitions"""
from abc import abstractmethod
from pathlib import Path
from typing import TypeVar

from pydantic import Field
from pydantic.types import DirectoryPath

from cppython_core.schema import DataPlugin, PluginGroupData, SyncData


class GeneratorGroupData(PluginGroupData):
    """Base class for the configuration data that is set by the project for the generator"""

    root_directory: DirectoryPath = Field(description="The directory where the pyproject.toml lives")


class Generator(DataPlugin[GeneratorGroupData]):
    """Abstract type to be inherited by CPPython Generator plugins"""

    @staticmethod
    @abstractmethod
    def supported(directory: Path) -> bool:
        """Queries a given directory for generator related files

        Args:
            directory: The directory to investigate

        Returns:
            Whether the directory has pre-existing generator support
        """
        raise NotImplementedError()

    @abstractmethod
    def sync(self, sync_data: SyncData) -> None:
        """Synchronizes generator files and state with the providers input

        Args:
            sync_data: List of information gathered from providers
        """
        raise NotImplementedError()


GeneratorT = TypeVar("GeneratorT", bound=Generator)
