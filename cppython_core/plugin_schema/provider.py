"""Provider data plugin definitions"""
from pathlib import Path
from typing import Protocol, TypeVar, runtime_checkable

from pydantic import Field
from pydantic.types import DirectoryPath

from cppython_core.schema import DataPlugin, PluginGroupData, PluginName, SyncData


class ProviderGroupData(PluginGroupData):
    """Base class for the configuration data that is set by the project for the provider"""

    root_directory: DirectoryPath = Field(description="The directory where the pyproject.toml lives")
    generator: str


@runtime_checkable
class Provider(DataPlugin[ProviderGroupData], Protocol):
    """Abstract type to be inherited by CPPython Provider plugins"""

    @staticmethod
    def supported(directory: Path) -> bool:
        """Queries a given directory for provider related files

        Args:
            directory: The directory to investigate

        Returns:
            Whether the directory has pre-existing provider support
        """
        raise NotImplementedError()

    @classmethod
    async def download_tooling(cls, path: Path) -> None:
        """Installs the external tooling required by the provider

        Args:
            path: The directory to download any extra tooling to

        Raises:
            NotImplementedError: Must be sub-classed
        """

    def sync_data(self, generator_name: PluginName) -> SyncData | None:
        """Requests generator information from the provider. The generator is either defined by a provider specific file
        or the CPPython configuration table

        Args:
            generator_name: The name of the generator requesting sync information

        Returns:
            An instantiated data type
        """

    def install(self) -> None:
        """Called when dependencies need to be installed from a lock file."""

    def update(self) -> None:
        """Called when dependencies need to be updated and written to the lock file."""


ProviderT = TypeVar("ProviderT", bound=Provider)
