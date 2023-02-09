"""Provider data plugin definitions"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar

from pydantic import Field
from pydantic.types import DirectoryPath

from cppython_core.schema import DataPlugin, PluginGroupData, PluginName, SyncData


class ProviderGroupData(PluginGroupData):
    """Base class for the configuration data that is set by the project for the provider"""

    root_directory: DirectoryPath = Field(description="The directory where the pyproject.toml lives")
    generator: str


class ProviderPlugin(DataPlugin[ProviderGroupData]):
    """Concrete Provider plugin type"""


class Provider(ProviderPlugin, ABC):
    """Abstract type to be inherited by CPPython Provider plugins"""

    @staticmethod
    @abstractmethod
    def supported(directory: Path) -> bool:
        """Queries a given directory for provider related files

        Args:
            directory: The directory to investigate

        Returns:
            Whether the directory has pre-existing provider support
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    async def download_tooling(cls, path: Path) -> None:
        """Installs the external tooling required by the provider

        Args:
            path: The directory to download any extra tooling to

        Raises:
            NotImplementedError: Must be sub-classed
        """

        raise NotImplementedError()

    @abstractmethod
    def sync_data(self, generator_name: PluginName) -> SyncData | None:
        """Requests generator information from the provider. The generator is either defined by a provider specific file
        or the CPPython configuration table

        Args:
            generator_name: The name of the generator requesting sync information

        Returns:
            An instantiated data type
        """
        raise NotImplementedError()

    @abstractmethod
    def install(self) -> None:
        """Called when dependencies need to be installed from a lock file."""
        raise NotImplementedError()

    @abstractmethod
    def update(self) -> None:
        """Called when dependencies need to be updated and written to the lock file."""
        raise NotImplementedError()


ProviderT = TypeVar("ProviderT", bound=Provider)
