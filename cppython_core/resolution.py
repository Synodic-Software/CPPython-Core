"""Data conversion routines"""

from typing import cast

from cppython_core.plugin_schema.generator import GeneratorData
from cppython_core.plugin_schema.provider import ProviderData
from cppython_core.plugin_schema.vcs import VersionControlData
from cppython_core.schema import (
    CPPythonData,
    CPPythonGlobalConfiguration,
    CPPythonLocalConfiguration,
    CPPythonPluginData,
    DataPluginT,
    PEP621Configuration,
    PEP621Data,
    ProjectData,
)


def resolve_pep621(pep621_configuration: PEP621Configuration, project_data: ProjectData) -> PEP621Data:
    """Creates a resolved type

    Args:
        pep621_configuration: Input PEP621 configuration
        project_data: The input configuration used to aid the resolve

    Raises:
        ValueError: Raised if there is a broken schema

    Returns:
        The resolved type
    """

    # Update the dynamic version
    if "version" in pep621_configuration.dynamic:
        modified_version = project_data.version

    elif pep621_configuration.version is not None:
        modified_version = pep621_configuration.version

    else:
        raise ValueError("Version can't be resolved. This is an internal schema error")

    pep621_data = PEP621Data(
        name=pep621_configuration.name, version=modified_version, description=pep621_configuration.description
    )
    return pep621_data


def resolve_cppython_plugin(cppython_data: CPPythonData, plugin_type: type[DataPluginT]) -> CPPythonPluginData:
    """Resolve project configuration for plugins
    TODO: Replace return type with Self

    Args:
        cppython_data: The CPPython data
        plugin_type: The type of the plugin

    Returns:
        The resolved type with provider specific modifications
    """

    # Add provider specific paths to the base path
    modified_install_path = cppython_data.install_path / plugin_type.name()
    modified_install_path.mkdir(parents=True, exist_ok=True)

    plugin_data = CPPythonData(
        install_path=modified_install_path,
        tool_path=cppython_data.tool_path,
        build_path=cppython_data.build_path,
        dependencies=cppython_data.dependencies,
        current_check=cppython_data.current_check,
    )

    return cast(CPPythonPluginData, plugin_data)


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

    cppython_data = CPPythonData(
        install_path=modified_install_path,
        tool_path=modified_tool_path,
        build_path=modified_build_path,
        dependencies=local_configuration.dependencies,
        current_check=global_configuration.current_check,
    )
    return cppython_data


def resolve_generator(project_data: ProjectData) -> GeneratorData:
    """Creates an instance from the given project

    Args:
        project_data: The input project configuration

    Returns:
        The plugin specific configuration
    """
    configuration = GeneratorData(root_directory=project_data.pyproject_file.parent)
    return configuration


def resolve_provider(project_data: ProjectData) -> ProviderData:
    """Creates an instance from the given project

    Args:
        project_data: The input project configuration

    Returns:
        The plugin specific configuration
    """
    configuration = ProviderData(root_directory=project_data.pyproject_file.parent)
    return configuration


def resolve_vcs(project_data: ProjectData) -> VersionControlData:
    """Creates an instance from the given project

    Args:
        project_data: The input project configuration

    Returns:
        The plugin specific configuration
    """
    configuration = VersionControlData(root_directory=project_data.pyproject_file.parent)
    return configuration