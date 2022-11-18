"""Interface plugin definitions"""
from abc import abstractmethod
from typing import TypeVar

from cppython_core.schema import Plugin


class Interface(Plugin):
    """Abstract type to be inherited by CPPython interfaces"""

    @staticmethod
    def cppython_group() -> str:
        """The cppython plugin group name. An EntryPoint sub-group
        Returns:
            The group name
        """
        return "interface"

    @abstractmethod
    def write_pyproject(self) -> None:
        """Called when CPPython requires the interface to write out pyproject.toml changes"""
        raise NotImplementedError()


InterfaceT = TypeVar("InterfaceT", bound=Interface)
