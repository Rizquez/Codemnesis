# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from pathlib import Path
from typing import TYPE_CHECKING, List, Dict, Set
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.utils.graphics import *
from src.utils.maps import *

if TYPE_CHECKING:
    from src.models import ModuleInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['generate_graph']

GRAPH_FILE = 'Graph'

def generate_graph(
    modules: List['ModuleInfo'], 
    output: str, 
    repository: str, 
    framework: str, 
    *, 
    format: str = 'svg'
) -> str:
    """
    Generates the dependency graph found between the analyzed modules.

    This method builds the internal dependency map of the code, invokes the generation of the corresponding graph, 
    and physically stores it in the user-defined path. The graph is generated according to the type of framework 
    evaluated, since each framework requires a different analysis of how the modules are structured.

    Args:
        modules (List[ModuleInfo]):
            List of `ModuleInfo` objects representing the analyzed modules in the repository.
        output (str):
            Path of the directory where the file will be stored. If it does not exist, it is created automatically.
        repository (str):
            Base path of the repository or project to be analyzed.
        framework (str):
            Name of the framework used, which must have a compatible mapping method.
        format (str, optional):
            Final format of the graph file.
    
    Returns:
        str:
            Absolute path of the generated output file.
    """
    dep_map: Dict[str, Set] = _build_map(modules, repository, framework)

    graph = map_to_graph(dep_map, format)

    out = Path(output) / f'{GRAPH_FILE}.{format}'

    graph.render(out.with_suffix(''), cleanup=True)

    return out

def _build_map(modules: List['ModuleInfo'], repository: str, framework: str) -> object:
    """
    Builds the dependency map according to the specified framework.

    This method locates the analysis function corresponding to the 
    declared framework and executes it to obtain the actual dependency 
    map between modules.

    If the framework does not have a valid mapping method, execution 
    is interrupted with an explicit error.

    Args:
        modules (List[ModuleInfo]):
            List of `ModuleInfo` objects representing the analyzed modules in the repository.
        repository (str):
            Base path of the repository or project to be analyzed.
        framework (str):
            Name of the framework used, which must have a compatible mapping method.

    Returns:
        object:
            Dependency structure produced by the corresponding mapping method.

    Raises:
        ValueError:
            When the framework does not have a registered compatible method.
    """
    paths = _get_paths(modules, repository)

    method = globals().get(f'{framework}_map')

    if method and callable(method):
        return method(modules, paths)
    else:
        raise ValueError(
            "Check the execution parameters!"
            f"The {framework} framework is not currently supported"
        )

def _get_paths(modules: List['ModuleInfo'], repository: str) -> Dict[str, str]:
    """
    Retrieves the logical module names along with their actual physical paths.

    This method translates the full file paths in the repository to extensionless 
    relative paths, and then converts these paths into a format fully compatible 
    with the standard way of importing modules.

    Args:
        modules (List[ModuleInfo]):
            List of `ModuleInfo` objects representing the analyzed modules in the repository.
        repository (str):
            Base path of the repository or project to be analyzed.

    Returns:
        Dict:
        Dictionary relating: importable_module_name → absolute_file_path
    """
    dct = {}

    root = Path(repository).resolve()
    for module in modules:
        relative = Path(module.path).resolve().relative_to(root)
        name = relative.with_suffix('').as_posix().replace('/', '.')
        dct[name] = module.path
    
    return dct

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE