"""Provider data plugin definitions"""
from typing import Any, Protocol, TypeVar, runtime_checkable

from pydantic import Field
from pydantic.types import DirectoryPath

from cppython_core.schema import (
    DataPlugin,
    ModelT,
    PluginGroupData,
    PluginName,
    SyncData,
)


class ProviderGroupData(PluginGroupData):
    """Base class for the configuration data that is set by the project for the provider"""

    root_directory: DirectoryPath = Field(description="The directory where the pyproject.toml lives")
    generator: str


@runtime_checkable
class Provider(DataPlugin[ProviderGroupData, ModelT], Protocol[ModelT]):
    """Abstract type to be inherited by CPPython Provider plugins"""

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


ProviderT = TypeVar("ProviderT", bound=Provider[Any])
