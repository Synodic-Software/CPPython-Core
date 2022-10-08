"""Provider data plugin definitions"""
from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import TypeVar

from pydantic import Field
from pydantic.types import DirectoryPath

from cppython_core.schema import DataPlugin, PluginGroupData


class ProviderData(PluginGroupData):
    """Base class for the configuration data that is set by the project for the provider"""

    root_directory: DirectoryPath = Field(description="The directory where the pyproject.toml lives")


class Provider(DataPlugin[ProviderData]):
    """Abstract type to be inherited by CPPython Provider plugins"""

    @staticmethod
    def group() -> str:
        """The plugin group name as used by 'setuptools'

        Returns:
            The group name
        """

        return "provider"

    @classmethod
    @abstractmethod
    def tooling_downloaded(cls, path: Path) -> bool:
        """Returns whether the provider tooling needs to be downloaded

        Args:
            path: The directory to check for downloaded tooling

        Raises:
            NotImplementedError: Must be sub-classed

        Returns:
            Whether the tooling has been downloaded or not
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
    def install(self) -> None:
        """Called when dependencies need to be installed from a lock file."""
        raise NotImplementedError()

    @abstractmethod
    def update(self) -> None:
        """Called when dependencies need to be updated and written to the lock file."""
        raise NotImplementedError()


ProviderT = TypeVar("ProviderT", bound=Provider)
