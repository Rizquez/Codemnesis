# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from typing import TYPE_CHECKING, List, Dict, Set
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.utils.paths import physical_path

if TYPE_CHECKING:
    from src.models import ModuleInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['dependencies_map', 'identifiers_map']

def dependencies_map(modules: List['ModuleInfo'], repository: str, framework: str) -> Dict[str, Set]:
    """
    Build the dependency map between modules based on analysis information and the logical 
    paths of the project.

    Args:
        modules (List[ModuleInfo]):
            List of `ModuleInfo` objects representing the analyzed modules in the repository.
        repository (str):
            Base path of the repository or project to be analyzed.
        framework (str):
            Name of the framework used, which must have a compatible mapping method.

    Returns:
        Dict:
            Dependency structure produced by the corresponding repository and framework.
    """
    paths = physical_path(modules, repository, framework)

    return _dependencies(modules, paths)

def identifiers_map(all_path: List[str]) -> Dict[str, str]:
    """
    Build a dictionary that assigns an internal identifier to each module.

    Because Graphviz doesn't work well with long paths or special characters within node 
    identifiers, this function generates simplified identifiers in the format: `m0`, `m1`, `m2`, `...`

    Args:
        all_path(List[str]):
            Alphabetically ordered list with all the unique paths detected.

    Returns:
        Dict:
            Dictionary where the keys are module paths and the values ​​are simplified identifiers.
    """
    return {path: f'm{idx}' for idx, path in enumerate(all_path)}

def _dependencies(modules: List['ModuleInfo'], paths: Dict[str, str]) -> Dict[str, Set[str]]:
    """
    Builds the actual dependency map between repository modules.

    This method analyzes all the imports declared by each module and determines, based on 
    the provided path dictionary, which physical module each import belongs to.
    
    The logic is based on progressively breaking down the import to locate the most specific 
    path available within the project.

    Recursive dependencies to the source module are not registered, so if a module imports 
    something that maps to itself, it will be ignored.

    Only the first valid candidate found for an import is considered, always starting with 
    the most specific one.

    Args:
        modules (List[ModuleInfo]):
            List of `ModuleInfo` objects representing the analyzed modules in the repository.
        paths (Dict[str, str]):
            Dictionary that relates package/module name to the physical path of the corresponding file.

    Returns:
        Dict:
            Dictionary where each key represents the path of the source module and each value is a set 
            with the paths of the imported modules that were successfully resolved.
    """
    dep_map = {module.path: set() for module in modules}

    for module in modules:
        src = module.path

        for imp in module.imports:
            candidates: List[str] = []
            parts = imp.split('.')

            while parts:
                candidates.append('.'.join(parts))
                parts.pop()

            target_paths: Set[str] = set()

            for candidate in candidates:
                if candidate in paths:
                    target_paths = paths[candidate]
                    break

            for path in target_paths:
                if path and path != src:
                    dep_map[src].add(path)

    return dep_map

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE