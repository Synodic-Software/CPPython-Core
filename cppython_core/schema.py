"""
Data types for CPPython that encapsulate the requirements between the plugins and the core library
"""

from abc import ABC, abstractmethod
from enum import Enum
from logging import Logger, getLogger
from pathlib import Path
from typing import Any, Generic, Optional, Type, TypeVar

from packaging.requirements import InvalidRequirement, Requirement
from pydantic import BaseModel, Extra, Field, validator


class CPPythonModel(BaseModel):
    """
    The base model to use for all CPPython models
    """

    class Config:
        """
        Pydantic built-in configuration
        """

        validate_assignment = True


ModelT = TypeVar("ModelT", bound=CPPythonModel)


class TargetEnum(Enum):
    """
    The C++ build target type
    """

    EXE = "executable"
    STATIC = "static"
    SHARED = "shared"


class PEP621(CPPythonModel):
    """
    CPPython relevant PEP 621 conforming data
    Because only the partial schema is used, we ignore 'extra' attributes
        Schema: https://www.python.org/dev/peps/pep-0621/
    """

    dynamic: list[str] = Field(default=[], description="https://peps.python.org/pep-0621/#dynamic")
    name: str = Field(description="https://peps.python.org/pep-0621/#name")
    version: Optional[str] = Field(default=None, description="https://peps.python.org/pep-0621/#version")
    description: str = Field(default="", description="https://peps.python.org/pep-0621/#description")

    @validator("version")
    def validate_version(value, values: dict[str, Any]):  # pylint: disable=E0213
        """
        TODO
        """

        if "version" in values["dynamic"]:
            assert value is None
        else:
            assert value is not None

        return value


ProjectDataT = TypeVar("ProjectDataT", bound=PEP621)


def _default_install_location() -> Path:

    return Path.home() / ".cppython"


class PEP508(Requirement):
    """
    PEP 508 conforming string
    """

    @classmethod
    def __get_validators__(cls):
        """
        TODO
        """
        yield cls.validate

    @classmethod
    def validate(cls, value: "PEP508"):
        """
        TODO
        """
        if not isinstance(value, str):
            raise TypeError("string required")

        try:
            definition = Requirement(value)
        except InvalidRequirement as invalid:
            raise ValueError from invalid

        return definition


class Preset(CPPythonModel):
    """
    Partial Preset specification
    """

    name: str
    hidden: Optional[bool] = Field(default=None)
    inherits: Optional[list[str] | str] = Field(default=None)
    displayName: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    cacheVariables: Optional[dict[str, None | bool | str | dict[str, str | bool]]] = Field(default=None)

    @validator("inherits")
    def validate_str(cls, values: Optional[list[str] | str]):  # pylint: disable=E0213
        """
        Conform to list
        """
        if isinstance(values, str):
            return [values]

        return values


class ConfigurePreset(Preset):
    """
    Partial Configure Preset specification
    """

    toolchainFile: Optional[str] = Field(default=None)

    @validator("toolchainFile")
    def validate_path(cls, value: Optional[str]):  # pylint: disable=E0213
        """
        TODO
        """
        if value is not None:
            return Path(value).as_posix()

        return None


class CPPythonData(CPPythonModel, extra=Extra.forbid):
    """
    Data required by the tool
    """

    target: TargetEnum
    dependencies: list[PEP508] = Field(default=[])
    install_path: Path = Field(default=_default_install_location(), alias="install-path")
    tool_path: Path = Field(default=Path("tool"), alias="tool-path")
    build_path: Path = Field(default=Path("build"), alias="build-path")


CPPythonDataT = TypeVar("CPPythonDataT", bound=CPPythonData)


class ToolData(CPPythonModel):
    """
    Tool entry
    This schema is not under our control. Ignore 'extra' attributes
    """

    cppython: Optional[CPPythonData] = Field(default=None)


ToolDataT = TypeVar("ToolDataT", bound=ToolData)


class PyProject(CPPythonModel):
    """
    pyproject.toml schema
    This schema is not under our control. Ignore 'extra' attributes
    """

    project: PEP621
    tool: Optional[ToolData] = Field(default=None)


PyProjectT = TypeVar("PyProjectT", bound=PyProject)


class Plugin(ABC):
    """
    Abstract plugin type
    """

    @abstractmethod
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    @abstractmethod
    def name() -> str:
        """
        The name of the plugin, canonicalized
        """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def group() -> str:
        """
        The plugin group name as used by 'setuptools'
        """
        raise NotImplementedError()

    @classmethod
    @property
    def logger(cls) -> Logger:
        """
        Returns the plugin specific sub-logger
        """

        if not hasattr(cls, "_logger"):
            cls._logger = getLogger(f"cppython.{cls.group()}.{cls.name()}")

        return cls._logger


PluginT = TypeVar("PluginT", bound=Plugin)


class InterfaceConfiguration(CPPythonModel, extra=Extra.forbid):
    """
    Base class for the configuration data that is passed to the interface
    """


class GeneratorConfiguration(CPPythonModel, extra=Extra.forbid):
    """
    Base class for the configuration data that is set by the project for the generator
    """

    root_path: Path = Field(description="The path where the pyproject.toml lives")


class GeneratorData(CPPythonModel, extra=Extra.forbid):
    """
    Base class for the configuration data that will be read by the interface and given to the generator
    """


GeneratorDataT = TypeVar("GeneratorDataT", bound=GeneratorData)


class Interface(Plugin):
    """
    Abstract type to be inherited by CPPython interfaces
    """

    @abstractmethod
    def __init__(self, configuration: InterfaceConfiguration) -> None:
        """
        TODO
        """
        self._configuration = configuration

        super().__init__()

    @property
    def configuration(self) -> InterfaceConfiguration:
        """
        TODO
        """
        return self._configuration

    @staticmethod
    @abstractmethod
    def name() -> str:
        """
        The name of the plugin, canonicalized
        """
        raise NotImplementedError()

    @staticmethod
    def group() -> str:
        """
        The plugin group name as used by 'setuptools'
        """
        return "interface"

    @abstractmethod
    def write_pyproject(self) -> None:
        """
        Called when CPPython requires the interface to write out pyproject.toml changes
        """
        raise NotImplementedError()


InterfaceT = TypeVar("InterfaceT", bound=Interface)


class Generator(Plugin, Generic[GeneratorDataT]):
    """
    Abstract type to be inherited by CPPython Generator plugins
    """

    @abstractmethod
    def __init__(
        self,
        configuration: GeneratorConfiguration,
        project: PEP621,
        cppython: CPPythonData,
        generator: GeneratorDataT,
    ) -> None:
        """
        Allows CPPython to pass the relevant data to constructed Generator plugin
        """
        self._configuration = configuration
        self._project = project
        self._cppython = cppython
        self._generator = generator

        super().__init__()

    @property
    def configuration(self) -> GeneratorConfiguration:
        """
        TODO
        """
        return self._configuration

    @property
    def project(self) -> PEP621:
        """
        TODO
        """
        return self._project

    @property
    def cppython(self) -> CPPythonData:
        """
        TODO
        """
        return self._cppython

    @property
    def generator(self) -> GeneratorDataT:
        """
        TODO
        """
        return self._generator

    @staticmethod
    def group() -> str:
        """
        The plugin group name as used by 'setuptools'
        """
        return "generator"

    @staticmethod
    @abstractmethod
    def name() -> str:
        """
        The string that is matched with the [tool.cppython.generator] string
        """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def data_type() -> Type[GeneratorDataT]:
        """
        Returns the pydantic type to cast the generator configuration data to
        """
        raise NotImplementedError()

    @abstractmethod
    def generator_downloaded(self, path: Path) -> bool:
        """
        Returns whether the generator needs to be downloaded
        """
        raise NotImplementedError()

    @abstractmethod
    def download_generator(self, path: Path) -> None:
        """
        Installs the external tooling required by the generator
        """
        raise NotImplementedError()

    @abstractmethod
    def update_generator(self, path: Path) -> None:
        """
        Update the tooling required by the generator
        """
        raise NotImplementedError()

    @abstractmethod
    def install(self) -> None:
        """
        Called when dependencies need to be installed from a lock file.
        """
        raise NotImplementedError()

    @abstractmethod
    def update(self) -> None:
        """
        Called when dependencies need to be updated and written to the lock file.
        """
        raise NotImplementedError()

    @abstractmethod
    def generate_cmake_config(self) -> ConfigurePreset:
        """
        Called when dependencies need to be updated and written to the lock file.

        @returns - A CMake configure preset
        """
        raise NotImplementedError()


# Generator[GeneratorDataT] is not allowed. 'Any' will resolve to GeneratorDataT when implemented
GeneratorT = TypeVar("GeneratorT", bound=Generator[Any])
