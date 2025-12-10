# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from pathlib import Path
from typing import TYPE_CHECKING, List, Dict, Set
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
if TYPE_CHECKING:
    from src.models import ModuleInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['physical_path', 'dependencies_path']

def physical_path(modules: List['ModuleInfo'], repository: str, framework: str) -> Dict[str, Set[str]]:
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
        framework (str):
            Name of the framework used, which must have a compatible mapping method.

    Returns:
        Dict:
            Dictionary where each key is a logical identifier and each value is a set of file 
            paths that implement it within the repository.

    Raises:
        ValueError:
            When the framework does not have a registered compatible method.
    """
    dct = {}

    root = Path(repository).resolve()

    for module in modules:
        if framework == 'csharp':
            for imp in getattr(module, 'imports', []):
                if imp.startswith('__ns__:'):
                    ns = imp[len('__ns__:'):]
                    dct.setdefault(ns, set()).add(module.path)
        elif framework == 'python':
            relative = Path(module.path).resolve().relative_to(root)
            name = relative.with_suffix('').as_posix().replace('/', '.')
            dct[name] = module.path
        else:
            raise ValueError(f"Check the execution parameters, the {framework} framework is not currently supported")
    
    return dct

def dependencies_path(dep_map: Dict[str, Set[str]]) -> List[str]:
    """
    This function retrieves the complete list of module paths present in the dependency map.

    **It extracts:**
        - all keys from the dictionary (source modules)
        - all values ​​for each key (target modules)

    Then it combines both sets, removes duplicates, and returns them sorted.

    Args:
        dep_map(Dict[str, Set[str]]): 
            Dictionary where each key is a module and its value is a set of modules on which 
            it depends.

    Returns:
        List: 
            Alphabetically ordered list with all the unique paths detected.
    """
    all_path = list(dep_map.keys())

    for path in dep_map.values():
        all_path.extend(list(path))

    return sorted(set(all_path))

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE