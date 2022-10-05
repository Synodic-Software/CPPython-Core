"""Data conversion routines"""

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


def cppython_plugin(cppython_data: CPPythonData, plugin_type: type[DataPluginT]) -> CPPythonPluginData:
    """Returns a deep copy that is modified for the given provider
    TODO: Replace return type with Self

    Args:
        cppython_data: The CPPython data
        plugin_type: The type of the plugin

    Returns:
        The resolved type with provider specific modifications
    """

    modified = cppython_data.copy(deep=True)

    # Add provider specific paths to the base path
    generator_install_path = modified.install_path / plugin_type.name()
    generator_install_path.mkdir(parents=True, exist_ok=True)
    modified.install_path = generator_install_path

    plugin_data = CPPythonPluginData()
    return plugin_data


def pep621(pep621_configuration: PEP621Configuration, project_data: ProjectData) -> PEP621Data:
    """Creates a self copy and resolves dynamic attributes

    Args:
        pep621_configuration: Input PEP621 configuration
        project_data: The input configuration used to aid the resolve

    Returns:
        The resolved copy
    """

    modified = pep621_configuration.copy(deep=True)

    # Update the dynamic version
    if "version" in modified.dynamic:
        modified.dynamic.remove("version")
        modified.version = project_data.version

    pep621_data = PEP621Data()
    return pep621_data


def cppython(
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

    modified = self.copy(deep=True)

    root_directory = project_data.pyproject_file.parent.absolute()

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

    cppython_data = CPPythonData()
    return cppython_data


def generator(project_data: ProjectData) -> GeneratorData:
    """Creates an instance from the given project

    Args:
        project_data: The input project configuration

    Returns:
        The plugin specific configuration
    """
    configuration = GeneratorData(root_directory=project_data.pyproject_file.parent)
    return configuration


def provider(project_data: ProjectData) -> ProviderData:
    """Creates an instance from the given project

    Args:
        project_data: The input project configuration

    Returns:
        The plugin specific configuration
    """
    configuration = ProviderData(root_directory=project_data.pyproject_file.parent)
    return configuration


def vcs(project_data: ProjectData) -> VersionControlData:
    """Creates an instance from the given project

    Args:
        project_data: The input project configuration

    Returns:
        The plugin specific configuration
    """
    configuration = VersionControlData(root_directory=project_data.pyproject_file.parent)
    return configuration
