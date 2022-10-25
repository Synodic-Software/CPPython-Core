"""Data types for CPPython that encapsulate the requirements between the plugins and the core library
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from logging import Logger, getLogger
from pathlib import Path
from typing import Any
from typing import Generator as TypingGenerator
from typing import Generic, NewType, Self, TypeVar

from packaging.requirements import InvalidRequirement, Requirement
from pydantic import BaseModel, Extra, Field, validator
from pydantic.types import DirectoryPath, FilePath


class CPPythonModel(BaseModel):
    """The base model to use for all CPPython models"""

    @dataclass
    class Config:
        """Pydantic built-in configuration"""

        # Data aliases should only exist for Configuration types. Constructors will never take aliases by field name
        allow_population_by_field_name = False

        # Mutation will happen via data resolution
        allow_mutation = False


class CPPythonConfigurationModel(BaseModel):
    """The model to use for all CPPython configuration models"""

    @dataclass
    class Config:
        """Pydantic built-in configuration"""

        # Data aliases should only exist for Configuration types. Constructors will never take aliases by field name
        allow_population_by_field_name = False


ModelT = TypeVar("ModelT", bound=CPPythonModel)


class ProjectData(CPPythonModel, extra=Extra.forbid):
    """Resolved data of 'ProjectConfiguration'"""

    pyproject_file: FilePath = Field(description="The path where the pyproject.toml exists")
    verbosity: int = Field(default=0, description="The verbosity level as an integer [0,2]")


class ProjectConfiguration(CPPythonConfigurationModel, extra=Extra.forbid):
    """Project-wide configuration"""

    pyproject_file: FilePath = Field(description="The path where the pyproject.toml exists")
    version: str | None = Field(
        description=(
            "The version number a 'dynamic' project version will resolve to. If not provided a CPPython project will"
            " initialize its VCS plugins to discover any available version"
        )
    )
    verbosity: int = Field(default=0, description="The verbosity level as an integer [0,2]")

    @validator("verbosity")
    @classmethod
    def min_max(cls, value: int) -> int:
        """Validator that clamps the input value

        Args:
            value: Input to validate

        Returns:
            The clamped input value
        """
        return min(max(value, 0), 2)

    @validator("pyproject_file")
    @classmethod
    def pyproject_name(cls, value: FilePath) -> FilePath:
        """Validator that verifies the name of the file

        Args:
            value: Input to validate

        Raises:
            ValueError: The given filepath is not named "pyproject.toml"

        Returns:
            The file path
        """

        if value.name != "pyproject.toml":
            raise ValueError('The given file is not named "pyproject.toml"')

        return value


class PEP621Data(CPPythonModel):
    """Resolved PEP621Configuration data"""

    name: str
    version: str
    description: str


class PEP621Configuration(CPPythonModel):
    """CPPython relevant PEP 621 conforming data
    Because only the partial schema is used, we ignore 'extra' attributes
        Schema: https://www.python.org/dev/peps/pep-0621/
    """

    dynamic: list[str] = Field(default=[], description="https://peps.python.org/pep-0621/#dynamic")
    name: str = Field(description="https://peps.python.org/pep-0621/#name")
    version: str | None = Field(default=None, description="https://peps.python.org/pep-0621/#version")
    description: str = Field(default="", description="https://peps.python.org/pep-0621/#description")

    @validator("version", always=True)
    @classmethod
    def dynamic_version(cls, value: str | None, values: dict[str, Any]) -> str | None:
        """Validates that version is present or that the name is present in the dynamic field

        Args:
            value: The input version
            values: All values of the Model prior to running this validation

        Raises:
            ValueError: If dynamic versioning is incorrect

        Returns:
            The validated input version
        """

        if "version" not in values["dynamic"]:
            if value is None:
                raise ValueError("'version' is not a dynamic field. It must be defined")
        else:
            if value is not None:
                raise ValueError("'version' is a dynamic field. It must not be defined")

        return value


def _default_install_location() -> Path:
    return Path.home() / ".cppython"


class PEP508(Requirement):
    """PEP 508 conforming string"""

    @classmethod
    def __get_validators__(cls) -> TypingGenerator[Callable[..., Any], None, None]:
        """Yields the set of validators defined for this type so pydantic can use them internally

        Yields:
            A new validator Callable
        """
        yield cls.validate_type
        yield cls.validate_construction

    @classmethod
    def validate_type(cls, value: Self) -> Self:
        """Enforce type that this class can be cast to a Requirement

        Args:
            value: The input value to validate

        Raises:
            TypeError: Raised if the input value is not the right type

        Returns:
            The validated input value
        """
        if not isinstance(value, str) and not isinstance(value, PEP508):
            raise TypeError("'str' or 'PEP508' type required")

        return value

    @classmethod
    def validate_construction(cls, value: Self) -> Self:
        """Enforce type that this class can be cast to a Requirement

        Args:
            value: The input value to validate

        Raises:
            ValueError: Raised if a PEP508 requirement can't be parsed

        Returns:
            The validated input value
        """
        if isinstance(value, str):
            try:
                value = PEP508(value)
            except InvalidRequirement as invalid:
                raise ValueError from invalid

        return value


class CPPythonData(CPPythonModel, extra=Extra.forbid):
    """Resolved CPPython data with local and global configuration"""

    dependencies: list[PEP508]
    install_path: DirectoryPath
    tool_path: DirectoryPath
    build_path: DirectoryPath
    current_check: bool

    @validator("install_path", "tool_path", "build_path")
    @classmethod
    def validate_absolute_path(cls, value: DirectoryPath) -> DirectoryPath:
        """Enforce the input is an absolute path

        Args:
            value: The input value

        Raises:
            ValueError: Raised if the input is not an absolute path

        Returns:
            The validated input value
        """
        if not value.is_absolute():
            raise ValueError("Absolute path required")

        return value


CPPythonPluginData = NewType("CPPythonPluginData", CPPythonData)


class SyncData(CPPythonModel):
    """Data that passes in a plugin sync"""

    name: str
    data: Any


class Plugin(ABC):
    """Abstract plugin type"""

    _logger: Logger

    @staticmethod
    @abstractmethod
    def name() -> str:
        """The name of the plugin"""
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def group() -> str:
        """The plugin group name"""
        raise NotImplementedError()

    @classmethod
    def logger(cls) -> Logger:
        """Returns the plugin specific sub-logger

        Returns:
            The plugin's named logger
        """

        if not hasattr(cls, "_logger"):
            cls._logger = getLogger(f"cppython.{cls.group()}.{cls.name()}")

        return cls._logger


PluginT = TypeVar("PluginT", bound=Plugin)


class PluginGroupData(CPPythonModel, ABC, extra=Extra.forbid):
    """Group data"""


PluginGroupDataT = TypeVar("PluginGroupDataT", bound=PluginGroupData)


class CorePluginData(CPPythonModel):
    """Core resolved data that will be passed to data plugins"""

    project_data: ProjectData
    pep621_data: PEP621Data
    cppython_data: CPPythonPluginData


class DataPlugin(Plugin, Generic[PluginGroupDataT]):
    """Abstract plugin type for internal CPPython data"""

    def __init__(self, group_data: PluginGroupDataT, core_data: CorePluginData) -> None:
        self._group_data = group_data
        self._core_data = core_data

    @property
    def group_data(self) -> PluginGroupDataT:
        """Returns the PluginGroupData object set at initialization"""
        return self._group_data

    @property
    def core_data(self) -> CorePluginData:
        """Returns the data object set at initialization"""
        return self._core_data

    def activate(self, data: dict[str, Any]) -> None:
        """Called when the plugin configuration data is available after initialization

        Args:
            data: Input configuration data the plugin needs to parse
        """
        raise NotImplementedError()


DataPluginT = TypeVar("DataPluginT", bound=DataPlugin[Any])


class CPPythonGlobalConfiguration(CPPythonModel, extra=Extra.forbid):
    """Global data extracted by the tool"""

    current_check: bool = Field(default=True, alias="current-check", description="Checks for a new CPPython version")


class CPPythonLocalConfiguration(CPPythonModel, extra=Extra.forbid):
    """Data required by the tool"""

    dependencies: list[PEP508] = Field(default=[], description="List of PEP508 dependencies")
    install_path: Path = Field(
        default=_default_install_location(), alias="install-path", description="The global install path for the project"
    )
    tool_path: Path = Field(
        default=Path("tool"), alias="tool-path", description="The local tooling path for the project"
    )
    build_path: Path = Field(
        default=Path("build"), alias="build-path", description="The local build path for the project"
    )
    provider: dict[str, dict[str, Any]] = Field(
        default={}, description="List of dynamically generated 'provider' plugin data"
    )
    generator: dict[str, dict[str, Any]] = Field(
        default={}, description="A dynamically generated 'generator' plugin's data"
    )

    def extract_plugin_data(self, plugin_type: type[DataPluginT]) -> dict[str, Any]:
        """Extracts a plugin data type from the CPPython table

        Args:
            plugin_type: The plugin type

        Raises:
            KeyError: If there is no plugin data with the given name

        Returns:
            The plugin data
        """

        attribute = getattr(self, plugin_type.group())
        data: dict[str, Any] = attribute[plugin_type.name()]

        return data


class ToolData(CPPythonModel):
    """Tool entry of pyproject.toml"""

    cppython: CPPythonLocalConfiguration | None = Field(default=None)


class PyProject(CPPythonModel):
    """pyproject.toml schema"""

    project: PEP621Configuration
    tool: ToolData | None = Field(default=None)


class CoreData(CPPythonModel):
    """Core resolved data that will be resolved"""

    project_data: ProjectData
    pep621_data: PEP621Data
    cppython_data: CPPythonData
