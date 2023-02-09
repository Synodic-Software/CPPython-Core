"""Interface plugin definitions"""
from abc import ABC, abstractmethod
from typing import TypeVar

from cppython_core.schema import Plugin


class InterfacePlugin(Plugin):
    """Concrete Interface plugin type"""


class Interface(InterfacePlugin, ABC):
    """Abstract type to be inherited by CPPython interfaces"""

    @abstractmethod
    def write_pyproject(self) -> None:
        """Called when CPPython requires the interface to write out pyproject.toml changes"""
        raise NotImplementedError()


InterfaceT = TypeVar("InterfaceT", bound=Interface)
