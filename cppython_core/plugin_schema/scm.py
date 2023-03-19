"""Version control data plugin definitions"""
from abc import abstractmethod
from typing import Protocol, TypeVar, runtime_checkable

from pydantic import DirectoryPath

from cppython_core.schema import Plugin, SupportedFeatures


class SupportedSCMFeatures(SupportedFeatures):
    """SCM plugin feature support"""


@runtime_checkable
class SCM(Plugin, Protocol):
    """Base class for version control systems"""

    @staticmethod
    @abstractmethod
    def features(directory: DirectoryPath) -> SupportedSCMFeatures:
        """Broadcasts the shared features of the SCM plugin to CPPython

        Args:
            directory: The root directory where features are evaluated

        Returns:
            The supported features
        """
        raise NotImplementedError

    @abstractmethod
    def version(self, directory: DirectoryPath) -> str:
        """Extracts the system's version metadata

        Args:
            directory: The input directory

        Returns:
            A version string
        """
        raise NotImplementedError

    def description(self) -> str | None:
        """Requests extraction of the project description

        Returns:
            Returns the project description, or none if unavailable
        """


SCMT = TypeVar("SCMT", bound=SCM)
