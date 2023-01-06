"""Generator data plugin definitions"""
from abc import abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import Field
from pydantic.types import DirectoryPath

from cppython_core.schema import DataPlugin, PluginGroupData, SyncDataT


class GeneratorGroupData(PluginGroupData):
    """Base class for the configuration data that is set by the project for the generator"""

    root_directory: DirectoryPath = Field(description="The directory where the pyproject.toml lives")


class Generator(DataPlugin[GeneratorGroupData], Generic[SyncDataT]):
    """Abstract type to be inherited by CPPython Generator plugins"""

    @staticmethod
    @abstractmethod
    def sync_data_type() -> type[SyncDataT]:
        """_summary_

        Raises:
            NotImplementedError: _description_

        Returns:
            _description_
        """
        raise NotImplementedError()

    @abstractmethod
    def sync(self, sync_data: list[SyncDataT]) -> None:
        """Synchronizes generator files and state with the providers input

        Args:
            sync_data: List of information gathered from providers
        """
        raise NotImplementedError()


GeneratorT = TypeVar("GeneratorT", bound=Generator[Any])
