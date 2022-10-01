"""Data types for CPPython that encapsulate the requirements between the plugins and the core library
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from logging import Logger, getLogger
from pathlib import Path
from typing import Any
from typing import Generator as TypingGenerator
from typing import Generic, TypeVar

from packaging.requirements import InvalidRequirement, Requirement
from pydantic import BaseModel, Extra, Field, validator
from pydantic.types import DirectoryPath, FilePath


class CPPythonModel(BaseModel):
    """The base model to use for all CPPython models"""

    @dataclass
    class Config:
        """Pydantic built-in configuration"""

        # Currently, there is no need for programmatically defined data outside tests.
        # Tests will validate via default values and then assignment.
        allow_population_by_field_name = False

        validate_assignment = True


ModelT = TypeVar("ModelT", bound=CPPythonModel)


class ProjectConfiguration(CPPythonModel, extra=Extra.forbid):
    """Project-wide configuration"""

    pyproject_file: FilePath = Field(description="The path where the pyproject.toml exists")
    version: str = Field(description="The version number a 'dynamic' project version will resolve to")
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


class PEP621Resolved(CPPythonModel):
    """PEP621 type with values of the PEP621 model after resolution"""

    name: str
    version: str
    description: str


class PEP621(CPPythonModel):
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

    def resolve(self, project_configuration: ProjectConfiguration) -> PEP621Resolved:
        """Creates a self copy and resolves dynamic attributes

        Args:
            project_configuration: The input configuration used to aid the resolve

        Returns:
            The resolved copy
        """

        modified = self.copy(deep=True)

        # Update the dynamic version
        if "version" in modified.dynamic:
            modified.dynamic.remove("version")
            modified.version = project_configuration.version

        return PEP621Resolved(**modified.dict())


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
        yield cls.validate_requirement
        yield cls.validate_cppython

    @classmethod
    def validate_requirement(cls, value: "PEP508") -> PEP508:
        """Enforce type that this class can be cast to a Requirement
        TODO - Use the Self type python 3.11

        Args:
            value: The input value to validate

        Raises:
            TypeError: Raised if the input value is not the right type
            ValueError: Raised if a PEP508 requirement can't be parsed

        Returns:
            The validated input value
        """
        if not isinstance(value, str):
            raise TypeError("string required")

        try:
            Requirement(value)
        except InvalidRequirement as invalid:
            raise ValueError from invalid

        return value

    @classmethod
    def validate_cppython(cls, value: "PEP508") -> PEP508:
        """TODO: Use for something
        TODO - Use the Self type python 3.11

        Args:
            value: The input value to validate

        Returns:
            The validated input value
        """

        return value


class CPPythonDataResolved(CPPythonModel, extra=Extra.forbid):
    """CPPythonData type with values of the CPPythonData model after resolution"""

    dependencies: list[PEP508]
    install_path: DirectoryPath
    tool_path: DirectoryPath
    build_path: DirectoryPath

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

    def resolve_plugin(
        self, provider_type: type[DataPlugin[PluginDataConfigurationT, PluginDataT, PluginDataResolvedT]]
    ) -> CPPythonDataResolved:
        """Returns a deep copy that is modified for the given provider
        TODO: Replace return type with Self

        Args:
            provider_type: The type of the provider

        Returns:
            The resolved type with provider specific modifications
        """

        modified = self.copy(deep=True)

        # Add provider specific paths to the base path
        generator_install_path = modified.install_path / provider_type.name()
        generator_install_path.mkdir(parents=True, exist_ok=True)
        modified.install_path = generator_install_path

        return modified


CPPythonDataResolvedT = TypeVar("CPPythonDataResolvedT", bound=CPPythonDataResolved)


class CPPythonData(CPPythonModel, extra=Extra.forbid):
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
        default={}, description="Optional list of dynamically generated 'provider' plugin data"
    )
    generator: dict[str, dict[str, Any]] = Field(
        default={}, description="Optional list of dynamically generated 'generator' plugin data"
    )
    vcs: dict[str, dict[str, Any]] = Field(
        default={}, description="Optional list of dynamically generated 'vcs' plugin data"
    )

    def resolve(self, project_configuration: ProjectConfiguration) -> CPPythonDataResolved:
        """Creates a copy and resolves dynamic attributes

        Args:
            project_configuration: Project information to aid in the resolution

        Returns:
            An instance of the resolved type
        """

        modified = self.copy(deep=True)

        root_directory = project_configuration.pyproject_file.parent.absolute()

        # Add the base path to all relative paths
        if not modified.install_path.is_absolute():
            modified.install_path = root_directory / modified.install_path

        if not modified.tool_path.is_absolute():
            modified.tool_path = root_directory / modified.tool_path

        if not modified.build_path.is_absolute():
            modified.build_path = root_directory / modified.build_path

        # Create directories if they do not exist
        modified.install_path.mkdir(parents=True, exist_ok=True)
        modified.tool_path.mkdir(parents=True, exist_ok=True)
        modified.build_path.mkdir(parents=True, exist_ok=True)

        # Delete the plugin attributes for the resolve
        del modified.provider
        del modified.generator
        del modified.vcs

        return CPPythonDataResolved(**modified.dict())

    def extract_plugin_data(self, plugin_type: type[DataPluginT], plugin_data_type: type[PluginDataT]) -> PluginDataT:
        """Extracts a plugin data type from the CPPython table

        Args:
            plugin_type: The plugin type
            plugin_data_type: The plugin data type

        Raises:
            KeyError: If there is no plugin data with the given name

        Returns:
            The plugin data
        """

        attribute = getattr(self, plugin_type.group())
        data = attribute[plugin_type.name()]

        return plugin_data_type(**data)


class ToolData(CPPythonModel):
    """Tool entry of pyproject.toml"""

    cppython: CPPythonData | None = Field(default=None)


ToolDataT = TypeVar("ToolDataT", bound=ToolData)


class PyProject(CPPythonModel):
    """pyproject.toml schema"""

    project: PEP621
    tool: ToolData | None = Field(default=None)


PyProjectT = TypeVar("PyProjectT", bound=PyProject)


class Plugin(ABC):
    """Abstract plugin type"""

    _logger: Logger

    @staticmethod
    @abstractmethod
    def name() -> str:
        """The name of the plugin, canonicalized"""
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def group() -> str:
        """The plugin group name as used by 'setuptools'"""
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


class PluginDataConfiguration(CPPythonModel, ABC, extra=Extra.forbid):
    """_summary_"""


PluginDataConfigurationT = TypeVar("PluginDataConfigurationT", bound=PluginDataConfiguration)


class PluginDataResolved(CPPythonModel, ABC, extra=Extra.forbid):
    """Base class for the configuration data that will be resolved from 'ProviderData'"""


PluginDataResolvedT = TypeVar("PluginDataResolvedT", bound=PluginDataResolved)


class PluginData(CPPythonModel, ABC, Generic[PluginDataResolvedT], extra=Extra.forbid):
    """_summary_"""

    @abstractmethod
    def resolve(self, project_configuration: ProjectConfiguration) -> PluginDataResolvedT:
        """Creates a copy and resolves dynamic attributes

        Args:
            project_configuration: The configuration data used to help the resolution

        Raises:
            NotImplementedError: Must be sub-classed

        Returns:
            The resolved data type
        """
        raise NotImplementedError()


PluginDataT = TypeVar("PluginDataT", bound=PluginData[Any])


class DataPlugin(Plugin, Generic[PluginDataConfigurationT, PluginDataT, PluginDataResolvedT]):
    """Abstract plugin type for internal CPPython data"""

    def __init__(
        self,
        configuration: PluginDataConfigurationT,
        project: PEP621Resolved,
        cppython: CPPythonDataResolved,
        generator: PluginDataResolvedT,
    ) -> None:
        self._configuration = configuration
        self._project = project
        self._cppython = cppython
        self._generator = generator

    @property
    def configuration(self) -> PluginDataConfigurationT:
        """Returns the GeneratorConfiguration object set at initialization"""
        return self._configuration

    @property
    def project(self) -> PEP621Resolved:
        """Returns the PEP621Resolved object set at initialization"""
        return self._project

    @property
    def cppython(self) -> CPPythonDataResolved:
        """Returns the CPPythonDataResolved object set at initialization"""
        return self._cppython

    @property
    def generator(self) -> PluginDataResolvedT:
        """Returns the GeneratorDataResolved object set at initialization"""
        return self._generator

    @staticmethod
    @abstractmethod
    def data_type() -> type[PluginDataT]:
        """Returns the pydantic type to cast the provider configuration data to"""
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def resolved_data_type() -> type[PluginDataResolvedT]:
        """Returns the pydantic type to cast the resolved provider configuration data to"""
        raise NotImplementedError()


DataPluginT = TypeVar("DataPluginT", bound=DataPlugin[Any, Any, Any])
