"""Version control data plugin definitions"""
from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import TypeVar

from pydantic import Field
from pydantic.types import DirectoryPath

from cppython_core.schema import DataPlugin, PluginGroupData


class VersionControlData(PluginGroupData):
    """Base class for the configuration data that is set by the project for the version control"""

    root_directory: DirectoryPath = Field(description="The directory where the pyproject.toml lives")


class VersionControl(DataPlugin[VersionControlData]):
    """Base class for version control systems"""

    @abstractmethod
    def is_repository(self, path: Path) -> bool:
        """Queries repository status of a path

        Args:
            path: The input path to query

        Returns:
            Whether the given path is a repository root
        """
        raise NotImplementedError()

    @abstractmethod
    def extract_version(self, path: Path) -> str:
        """Extracts the system's version metadata

        Args:
            path: The repository path

        Returns:
            A version
        """
        raise NotImplementedError()

    @staticmethod
    def group() -> str:
        """The plugin group name as used by 'setuptools'summary

        Returns:
            The group name
        """
        return "vcs"


VersionControlT = TypeVar("VersionControlT", bound=VersionControl)
