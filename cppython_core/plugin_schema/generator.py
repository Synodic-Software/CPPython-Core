"""Generator data plugin definitions"""
from abc import abstractmethod
from typing import Any, Protocol, TypeVar, runtime_checkable

from pydantic import Field
from pydantic.types import DirectoryPath

from cppython_core.schema import CorePluginData, DataPlugin, PluginGroupData, SyncData


class GeneratorGroupData(PluginGroupData):
    """Base class for the configuration data that is set by the project for the generator"""

    root_directory: DirectoryPath = Field(description="The directory where the pyproject.toml lives")


class SyncConsumer(Protocol):
    """Interface for consuming synchronization data from providers"""

    @staticmethod
    @abstractmethod
    def sync_types() -> list[type[SyncData]]:
        """Broadcasts supported types

        Returns:
            A list of synchronization types that are supported
        """
        raise NotImplementedError

    @abstractmethod
    def sync(self, sync_data: SyncData) -> None:
        """Synchronizes generator files and state with the providers input

        Args:
            sync_data: The input data to sync with
        """
        raise NotImplementedError


@runtime_checkable
class Generator(DataPlugin, SyncConsumer, Protocol):
    """Abstract type to be inherited by CPPython Generator plugins"""

    @abstractmethod
    def __init__(
        self, group_data: GeneratorGroupData, core_data: CorePluginData, configuration_data: dict[str, Any]
    ) -> None:
        raise NotImplementedError


GeneratorT = TypeVar("GeneratorT", bound=Generator)
