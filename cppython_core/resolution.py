"""Data conversion routines"""

from pathlib import Path
from typing import cast

from pydantic import DirectoryPath
from synodic_utilities.utility import TypeName

from cppython_core.plugin_schema.generator import Generator, GeneratorPluginGroupData
from cppython_core.plugin_schema.provider import Provider, ProviderPluginGroupData
from cppython_core.plugin_schema.scm import SCM, SCMPluginGroupData
from cppython_core.schema import (
    CorePluginData,
    CPPythonData,
    CPPythonGlobalConfiguration,
    CPPythonLocalConfiguration,
    CPPythonModel,
    CPPythonPluginData,
    PEP621Configuration,
    PEP621Data,
    Plugin,
    ProjectConfiguration,
    ProjectData,
)


def resolve_project_configuration(project_configuration: ProjectConfiguration) -> ProjectData:
    """Creates a resolved type

    Args:
        project_configuration: Input configuration

    Returns:
        The resolved data
    """
    return ProjectData(pyproject_file=project_configuration.pyproject_file, verbosity=project_configuration.verbosity)


def resolve_pep621(
    pep621_configuration: PEP621Configuration, project_configuration: ProjectConfiguration, scm: SCM | None
) -> PEP621Data:
    """Creates a resolved type

    Args:
        pep621_configuration: Input PEP621 configuration
        project_configuration: The input configuration used to aid the resolve
        scm: SCM

    Raises:
        ConfigError: Raised when the tooling did not satisfy the configuration request
        ValueError: Raised if there is a broken schema

    Returns:
        The resolved type
    """

    # Update the dynamic version
    if "version" in pep621_configuration.dynamic:
        if project_configuration.version is not None:
            modified_version = project_configuration.version
        elif scm is not None:
            modified_version = scm.version(project_configuration.pyproject_file.parent)
        else:
            raise ValueError("Version can't be resolved. No SCM")

    elif pep621_configuration.version is not None:
        modified_version = pep621_configuration.version

    else:
        raise ValueError("Version can't be resolved. Schema error")

    pep621_data = PEP621Data(
        name=pep621_configuration.name, version=modified_version, description=pep621_configuration.description
    )
    return pep621_data


class PluginBuildData(CPPythonModel):
    """Data needed to construct CoreData"""

    generator_type: type[Generator]
    provider_type: type[Provider]
    scm_type: type[SCM]


class PluginCPPythonData(CPPythonModel):
    """Plugin data needed to construct CPPythonData"""

    generator_name: TypeName
    provider_name: TypeName
    scm_name: TypeName


def resolve_cppython(
    local_configuration: CPPythonLocalConfiguration,
    global_configuration: CPPythonGlobalConfiguration,
    project_data: ProjectData,
    plugin_build_data: PluginCPPythonData,
) -> CPPythonData:
    """Creates a copy and resolves dynamic attributes

    Args:
        local_configuration: Local project configuration
        global_configuration: Shared project configuration
        project_data: Project information to aid in the resolution
        plugin_build_data: Plugin build data

    Raises:
        ConfigError: Raised when the tooling did not satisfy the configuration request

    Returns:
        An instance of the resolved type
    """

    root_directory = project_data.pyproject_file.parent.absolute()

    # Add the base path to all relative paths
    modified_install_path = local_configuration.install_path

    if not modified_install_path.is_absolute():
        modified_install_path = root_directory / modified_install_path

    modified_tool_path = local_configuration.tool_path

    if not modified_tool_path.is_absolute():
        modified_tool_path = root_directory / modified_tool_path

    modified_build_path = local_configuration.build_path

    if not modified_build_path.is_absolute():
        modified_build_path = root_directory / modified_build_path

    # Create directories if they do not exist
    modified_install_path.mkdir(parents=True, exist_ok=True)
    modified_tool_path.mkdir(parents=True, exist_ok=True)
    modified_build_path.mkdir(parents=True, exist_ok=True)

    modified_provider_name = local_configuration.provider_name
    modified_generator_name = local_configuration.generator_name

    if modified_provider_name is None:
        modified_provider_name = plugin_build_data.provider_name

    if modified_generator_name is None:
        modified_generator_name = plugin_build_data.generator_name

    modified_scm_name = plugin_build_data.scm_name

    cppython_data = CPPythonData(
        install_path=modified_install_path,
        tool_path=modified_tool_path,
        build_path=modified_build_path,
        current_check=global_configuration.current_check,
        provider_name=modified_provider_name,
        generator_name=modified_generator_name,
        scm_name=modified_scm_name,
    )
    return cppython_data


def resolve_cppython_plugin(cppython_data: CPPythonData, plugin_type: type[Plugin]) -> CPPythonPluginData:
    """Resolve project configuration for plugins

    Args:
        cppython_data: The CPPython data
        plugin_type: The plugin type

    Returns:
        The resolved type with plugin specific modifications
    """

    # Add plugin specific paths to the base path
    modified_install_path = cppython_data.install_path / plugin_type.name()
    modified_install_path.mkdir(parents=True, exist_ok=True)

    plugin_data = CPPythonData(
        install_path=modified_install_path,
        tool_path=cppython_data.tool_path,
        build_path=cppython_data.build_path,
        current_check=cppython_data.current_check,
        provider_name=cppython_data.provider_name,
        generator_name=cppython_data.generator_name,
        scm_name=cppython_data.scm_name,
    )

    return cast(CPPythonPluginData, plugin_data)


def _write_tool_directory(core_data: CorePluginData, directory: Path) -> DirectoryPath:
    """Creates directories following a certain format

    Args:
        core_data: The core data
        plugin_path: The relative plugin path to use

    Returns:
        The written path
    """

    plugin_directory = core_data.cppython_data.tool_path / "cppython" / directory
    plugin_directory.mkdir(parents=True, exist_ok=True)

    return plugin_directory


def resolve_generator(core_data: CorePluginData) -> GeneratorPluginGroupData:
    """Creates an instance from the given project

    Args:
        core_data: The input project configuration

    Returns:
        The plugin specific configuration
    """

    root_directory = core_data.project_data.pyproject_file.parent
    tool_directory = _write_tool_directory(core_data, Path("generators") / core_data.cppython_data.generator_name)
    configuration = GeneratorPluginGroupData(root_directory=root_directory, tool_directory=tool_directory)
    return configuration


def resolve_provider(core_data: CorePluginData) -> ProviderPluginGroupData:
    """Creates an instance from the given project

    Args:
        core_data: The input project configuration

    Returns:
        The plugin specific configuration
    """

    root_directory = core_data.project_data.pyproject_file.parent
    tool_directory = _write_tool_directory(core_data, Path("providers") / core_data.cppython_data.provider_name)
    configuration = ProviderPluginGroupData(root_directory=root_directory, tool_directory=tool_directory)
    return configuration


def resolve_scm(core_data: CorePluginData) -> SCMPluginGroupData:
    """Creates an instance from the given project

    Args:
        core_data: The input project configuration

    Returns:
        The plugin specific configuration
    """

    root_directory = core_data.project_data.pyproject_file.parent
    tool_directory = _write_tool_directory(core_data, Path("managers") / core_data.cppython_data.scm_name)
    configuration = SCMPluginGroupData(root_directory=root_directory, tool_directory=tool_directory)
    return configuration
