"""Interface plugin definitions"""
from __future__ import annotations

from abc import abstractmethod
from typing import TypeVar

from cppython_core.schema import Plugin


class Interface(Plugin):
    """Abstract type to be inherited by CPPython interfaces"""

    @staticmethod
    def group() -> str:
        """Plugin group name

        Returns:
            Name
        """
        return "interface"

    @abstractmethod
    def write_pyproject(self) -> None:
        """Called when CPPython requires the interface to write out pyproject.toml changes"""
        raise NotImplementedError()


InterfaceT = TypeVar("InterfaceT", bound=Interface)
