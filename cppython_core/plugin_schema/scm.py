"""Version control data plugin definitions"""
from abc import abstractmethod
from pathlib import Path
from typing import Protocol, TypeVar, runtime_checkable

from cppython_core.schema import Plugin


@runtime_checkable
class SCM(Plugin, Protocol):
    """Base class for version control systems"""

    @abstractmethod
    def version(self, path: Path) -> str:
        """Extracts the system's version metadata

        Args:
            path: The input directory

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
