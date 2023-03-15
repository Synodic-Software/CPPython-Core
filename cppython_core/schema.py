"""Data types for CPPython that encapsulate the requirements between the plugins and the core library
"""

from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NewType, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel, Extra, Field, validator
from pydantic.types import DirectoryPath, FilePath


class CPPythonModel(BaseModel):
    """The base model to use for all CPPython models"""

    @dataclass
    class Config:
        """Pydantic built-in configuration"""

        # Data aliases should only exist for Configuration types, which will be read from files.
        #    Constructors will never take aliases by field name
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
            " initialize its SCM plugins to discover any available version"
        )
    )
    verbosity: int = Field(default=0, description="The verbosity level as an integer [0,2]")
    debug: bool = Field(
        default=False, description="Debug mode. Additional processing will happen to expose more debug information"
    )

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


class CPPythonData(CPPythonModel, extra=Extra.forbid):
    """Resolved CPPython data with local and global configuration"""

    install_path: DirectoryPath
    tool_path: DirectoryPath
    build_path: DirectoryPath
    current_check: bool
    provider_name: str
    generator_name: str

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

PluginName = NewType("PluginName", str)
PluginGroup = NewType("PluginGroup", str)
PluginFullName = NewType("PluginFullName", str)


class SyncData(CPPythonModel):
    """Data that passes in a plugin sync"""

    provider_name: PluginName


SyncDataT = TypeVar("SyncDataT", bound=SyncData)


class Information(CPPythonModel):
    """Plugin feature support"""

    initialization: bool = Field(
        default=False, description="Whether the plugin supports initialization from an empty state"
    )


@runtime_checkable
class Plugin(Protocol):
    """CPPython plugin"""

    @staticmethod
    def supported(directory: Path) -> bool:
        """Queries a given directory for plugin related files.
        If no meaningful plugin specific files are stored, the directory is in an unsupported state

        Args:
            directory: The directory to query

        Returns:
            Whether the directory has pre-existing plugin support.
        """
        return False

    @staticmethod
    @abstractmethod
    def information() -> Information:
        """Returns plugin information that broadcast the plugin's features"""
        raise NotImplementedError


PluginT = TypeVar("PluginT", bound=Plugin)


class PluginGroupData(CPPythonModel, extra=Extra.forbid):
    """Group data"""


PluginGroupDataT = TypeVar("PluginGroupDataT", bound=PluginGroupData)


class CorePluginData(CPPythonModel):
    """Core resolved data that will be passed to data plugins"""

    project_data: ProjectData
    pep621_data: PEP621Data
    cppython_data: CPPythonPluginData


class DataPlugin(Plugin, Protocol):
    """Abstract plugin type for internal CPPython data"""

    @abstractmethod
    def __init__(
        self, group_data: PluginGroupData, core_data: CorePluginData, configuration_data: dict[str, Any]
    ) -> None:
        raise NotImplementedError

    @classmethod
    async def download_tooling(cls, path: Path) -> None:
        """Installs the external tooling required by the plugin. Should be overridden if required

        Args:
            path: The directory to download any extra tooling to
        """


DataPluginT = TypeVar("DataPluginT", bound=DataPlugin)


class CPPythonGlobalConfiguration(CPPythonModel, extra=Extra.forbid):
    """Global data extracted by the tool"""

    current_check: bool = Field(default=True, alias="current-check", description="Checks for a new CPPython version")


ProviderData = NewType("ProviderData", dict[str, Any])
GeneratorData = NewType("GeneratorData", dict[str, Any])


class CPPythonLocalConfiguration(CPPythonModel, extra=Extra.forbid):
    """Data required by the tool"""

    install_path: Path = Field(
        default=_default_install_location(), alias="install-path", description="The global install path for the project"
    )
    tool_path: Path = Field(
        default=Path("tool"), alias="tool-path", description="The local tooling path for the project"
    )
    build_path: Path = Field(
        default=Path("build"), alias="build-path", description="The local build path for the project"
    )
    provider: ProviderData = Field(
        default=ProviderData({}), description="Provider plugin data associated with 'provider_name"
    )
    provider_name: str | None = Field(
        default=None, alias="provider-name", description="If empty, the provider will be automatically deduced."
    )
    generator: GeneratorData = Field(
        default=GeneratorData({}), description="Generator plugin data associated with 'generator_name'"
    )
    generator_name: str | None = Field(
        default=None, alias="generator-name", description="If empty, the generator will be automatically deduced."
    )


class ToolData(CPPythonModel):
    """Tool entry of pyproject.toml"""

    cppython: CPPythonLocalConfiguration = Field(description="CPPython tool data")


class PyProject(CPPythonModel):
    """pyproject.toml schema"""

    project: PEP621Configuration = Field(description="PEP621: https://www.python.org/dev/peps/pep-0621/")
    tool: ToolData = Field(description="Tool data")


class PluginBuildData(CPPythonModel):
    """Data needed to construct CoreData"""

    generator_type: type[Plugin]
    provider_type: type[Plugin]


class CoreData(CPPythonModel):
    """Core resolved data that will be resolved"""

    project_data: ProjectData
    pep621_data: PEP621Data
    cppython_data: CPPythonData


class Interface(Protocol):
    """Type for interfaces to allow feedback from CPPython"""

    @abstractmethod
    def write_pyproject(self) -> None:
        """Called when CPPython requires the interface to write out pyproject.toml changes"""
        raise NotImplementedError

    @abstractmethod
    def write_configuration(self) -> None:
        """Called when CPPython requires the interface to write out configuration changes"""
        raise NotImplementedError


InterfaceT = TypeVar("InterfaceT", bound=Interface)
