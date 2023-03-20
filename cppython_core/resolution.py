"""Data conversion routines"""

from typing import Any, cast

from cppython_core.plugin_schema.generator import Generator, GeneratorPluginGroupData
from cppython_core.plugin_schema.provider import Provider, ProviderPluginGroupData
from cppython_core.plugin_schema.scm import SCM, SCMPluginGroupData
from cppython_core.schema import (
    CPPythonData,
    CPPythonGlobalConfiguration,
    CPPythonLocalConfiguration,
    CPPythonModel,
    CPPythonPluginData,
    DataPlugin,
    PEP621Configuration,
    PEP621Data,
    PluginFullName,
    PluginGroup,
    PluginName,
    ProjectConfiguration,
    ProjectData,
)
from cppython_core.utility import canonicalize_name


def resolve_full_name(input_type: type[Any]) -> PluginFullName:
    """Concatenates group and name values
    Args:
        input_type: The input type to resolve
    Raises:
        ValueError: When the class name is incorrect
    Returns:
        Concatenated name
    """
    name = canonicalize_name(input_type.__name__)
    return PluginFullName(".".join(name))


def resolve_name(input_type: type[Any]) -> PluginName:
    """The plugin name
    Args:
        input_type: The input type to resolve
    Returns:
        The name
    """
    name = canonicalize_name(input_type.__name__)
    return PluginName(name.name)


def resolve_group(input_type: type[Any]) -> PluginGroup:
    """The cppython plugin group name
    Args:
        input_type: The input type to resolve
    Returns:
        The group name
    """
    name = canonicalize_name(input_type.__name__)
    return PluginGroup(name.group)


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


def resolve_cppython(
    local_configuration: CPPythonLocalConfiguration,
    global_configuration: CPPythonGlobalConfiguration,
    project_data: ProjectData,
    plugin_build_data: PluginBuildData,
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
        modified_provider_name = resolve_name(plugin_build_data.provider_type)

    if modified_generator_name is None:
        modified_generator_name = resolve_name(plugin_build_data.generator_type)

    cppython_data = CPPythonData(
        install_path=modified_install_path,
        tool_path=modified_tool_path,
        build_path=modified_build_path,
        current_check=global_configuration.current_check,
        provider_name=modified_provider_name,
        generator_name=modified_generator_name,
    )
    return cppython_data


def resolve_cppython_plugin(cppython_data: CPPythonData, plugin_type: type[DataPlugin]) -> CPPythonPluginData:
    """Resolve project configuration for plugins

    Args:
        cppython_data: The CPPython data
        plugin_type: The plugin type

    Returns:
        The resolved type with plugin specific modifications
    """

    # Add plugin specific paths to the base path
    modified_install_path = cppython_data.install_path / resolve_name(plugin_type)
    modified_install_path.mkdir(parents=True, exist_ok=True)

    plugin_data = CPPythonData(
        install_path=modified_install_path,
        tool_path=cppython_data.tool_path,
        build_path=cppython_data.build_path,
        current_check=cppython_data.current_check,
        provider_name=cppython_data.provider_name,
        generator_name=cppython_data.generator_name,
    )

    return cast(CPPythonPluginData, plugin_data)


def resolve_generator(project_data: ProjectData) -> GeneratorPluginGroupData:
    """Creates an instance from the given project

    Args:
        project_data: The input project configuration

    Returns:
        The plugin specific configuration
    """
    configuration = GeneratorPluginGroupData(root_directory=project_data.pyproject_file.parent)
    return configuration


def resolve_provider(project_data: ProjectData) -> ProviderPluginGroupData:
    """Creates an instance from the given project

    Args:
        project_data: The input project configuration

    Returns:
        The plugin specific configuration
    """
    configuration = ProviderPluginGroupData(root_directory=project_data.pyproject_file.parent)
    return configuration


def resolve_scm(project_data: ProjectData) -> SCMPluginGroupData:
    """Creates an instance from the given project

    Args:
        project_data: The input project configuration

    Returns:
        The plugin specific configuration
    """

    configuration = SCMPluginGroupData(root_directory=project_data.pyproject_file.parent)
    return configuration
