# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from typing import TYPE_CHECKING, List, Dict, Set
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
if TYPE_CHECKING:
    from src.models import ModuleInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['dependencies_map']

def dependencies_map(modules: List['ModuleInfo'], paths: Dict[str, str]) -> Dict[str, Set]:
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

            while len(parts) > 0:
                candidates.append('.'.join(parts))
                parts.pop()

            path = None
            for candidate in candidates:
                if candidate in paths:
                    path = paths[candidate]
                    break
            
            if path and path != src:
                dep_map[src].add(path)
    
    return dep_map

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE