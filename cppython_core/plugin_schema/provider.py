"""Provider data plugin definitions"""
from abc import abstractmethod
from typing import Protocol, TypeVar, runtime_checkable

from pydantic import Field
from pydantic.types import DirectoryPath

from cppython_core.schema import DataPlugin, PluginGroupData, SyncData


class ProviderGroupData(PluginGroupData):
    """Base class for the configuration data that is set by the project for the provider"""

    root_directory: DirectoryPath = Field(description="The directory where the pyproject.toml lives")
    generator: str


class SyncProducer(Protocol):
    """Interface for producing synchronization data with generators"""

    @abstractmethod
    def supported_sync_type(self, sync_type: type[SyncData]) -> bool:
        """Queries for support for a given synchronization type

        Args:
            sync_type: The type to query support for

        Returns:
            Support
        """
        raise NotImplementedError

    @abstractmethod
    def sync_data(self, sync_type: type[SyncData]) -> SyncData | None:
        """Requests generator information from the provider. The generator is either defined by a provider specific file
        or the CPPython configuration table

        Args:
            sync_type: The type requesting to be fulfilled

        Returns:
            An instantiated data type, or None if no instantiation is made
        """
        raise NotImplementedError


@runtime_checkable
class Provider(DataPlugin[ProviderGroupData], SyncProducer, Protocol):
    """Abstract type to be inherited by CPPython Provider plugins"""

    @abstractmethod
    def install(self) -> None:
        """Called when dependencies need to be installed from a lock file."""
        raise NotImplementedError

    @abstractmethod
    def update(self) -> None:
        """Called when dependencies need to be updated and written to the lock file."""
        raise NotImplementedError


ProviderT = TypeVar("ProviderT", bound=Provider)
