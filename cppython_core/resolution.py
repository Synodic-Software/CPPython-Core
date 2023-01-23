"""Data conversion routines"""

from typing import Any, cast

from cppython_core.exceptions import ConfigError
from cppython_core.plugin_schema.generator import Generator, GeneratorGroupData
from cppython_core.plugin_schema.provider import Provider, ProviderGroupData
from cppython_core.schema import (
    CPPythonData,
    CPPythonGlobalConfiguration,
    CPPythonLocalConfiguration,
    CPPythonPluginData,
    DataPlugin,
    PEP621Configuration,
    PEP621Data,
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
    pep621_configuration: PEP621Configuration, project_configuration: ProjectConfiguration
) -> PEP621Data:
    """Creates a resolved type

    Args:
        pep621_configuration: Input PEP621 configuration
        project_configuration: The input configuration used to aid the resolve

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
        else:
            raise ConfigError("'version' is dynamic but the interface did not provide a version value")

    elif pep621_configuration.version is not None:
        modified_version = pep621_configuration.version

    else:
        raise ValueError("Version can't be resolved. This is an internal schema error")

    pep621_data = PEP621Data(
        name=pep621_configuration.name, version=modified_version, description=pep621_configuration.description
    )
    return pep621_data


def resolve_cppython(
    local_configuration: CPPythonLocalConfiguration,
    global_configuration: CPPythonGlobalConfiguration,
    project_data: ProjectData,
) -> CPPythonData:
    """Creates a copy and resolves dynamic attributes

    Args:
        local_configuration: Local project configuration
        global_configuration: Shared project configuration
        project_data: Project information to aid in the resolution

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

    if local_configuration.provider_name is None:
        raise ConfigError("CPPython did not fill the 'provider_name' value")

    if local_configuration.generator_name is None:
        raise ConfigError("CPPython did not fill the 'generator_name' value")

    cppython_data = CPPythonData(
        install_path=modified_install_path,
        tool_path=modified_tool_path,
        build_path=modified_build_path,
        current_check=global_configuration.current_check,
        provider_name=local_configuration.provider_name,
        generator_name=local_configuration.generator_name,
    )
    return cppython_data


def resolve_cppython_plugin(cppython_data: CPPythonData, plugin_type: type[DataPlugin[Any]]) -> CPPythonPluginData:
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
    )

    return cast(CPPythonPluginData, plugin_data)


def resolve_generator(project_data: ProjectData) -> GeneratorGroupData:
    """Creates an instance from the given project

    Args:
        project_data: The input project configuration

    Returns:
        The plugin specific configuration
    """
    configuration = GeneratorGroupData(root_directory=project_data.pyproject_file.parent)
    return configuration


def resolve_provider(project_data: ProjectData, cppython_data: CPPythonData) -> ProviderGroupData:
    """Creates an instance from the given project

    Args:
        project_data: The input project configuration
        cppython_data: TODO

    Returns:
        The plugin specific configuration
    """
    configuration = ProviderGroupData(
        root_directory=project_data.pyproject_file.parent, generator=cppython_data.generator_name
    )
    return configuration


def extract_provider_data(cppython_local_configuration: CPPythonLocalConfiguration, plugin: Provider) -> dict[str, Any]:
    """Extracts a plugin data type from the CPPython table

    Args:
        cppython_local_configuration: Configuration data
        plugin: The plugin

    Raises:
        KeyError: If there is no plugin data with the given name

    Returns:
        The plugin data
    """

    data: dict[str, Any] = cppython_local_configuration.provider[plugin.name()]

    return data


def extract_generator_data(
    cppython_local_configuration: CPPythonLocalConfiguration, plugin: Generator
) -> dict[str, Any]:
    """Extracts a plugin data type from the CPPython table

    Args:
        cppython_local_configuration: Configuration data
        plugin: The plugin

    Raises:
        KeyError: If there is no plugin data with the given name

    Returns:
        The plugin data
    """

    data: dict[str, Any] = cppython_local_configuration.generator[plugin.name()]

    return data
