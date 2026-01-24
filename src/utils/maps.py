# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

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

def dependencies_map(modules: List[ModuleInfo], repository: str, framework: str) -> Dict[str, Set[str]]:
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
    paths = _physical_paths(modules, repository, framework)
    return _resolve_imports(modules, paths)

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

def _resolve_imports(modules: List[ModuleInfo], paths: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
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
        paths (Dict[str, Set[str]]):
            Dictionary that relates package/module name to the physical path of the corresponding file.

    Returns:
        Dict:
            Dictionary where each key represents the path of the source module and each value is a set 
            with the paths of the imported modules that were successfully resolved.
    """
    dep_map = {module.path: set() for module in modules} # Each module will have a set of dependencies

    for module in modules:
        src = module.path

        for imp in module.imports:
            candidates: List[str] = []

            # Candidates are generated from the complete import to its shortest form
            parts = imp.split('.')
            while parts:
                candidates.append('.'.join(parts))
                parts.pop()

            target_paths: Set[str] = set()

            for candidate in candidates:
                if candidate in paths:
                    target_paths = paths[candidate]
                    break
            
            # Each valid dependency is recorded
            for path in target_paths:
                if path and path != src:
                    dep_map[src].add(path)

    return dep_map

def _physical_paths(modules: List[ModuleInfo], repository: str, framework: str) -> Dict[str, Set[str]]:
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

    for module in modules:
        if framework == 'csharp': # Imports are prefixed with __ns__: to distinguish them from regular imports
            for imp in getattr(module, 'imports', []):
                if imp.startswith('__ns__:'):
                    ns = imp[len('__ns__:'):]
                    dct.setdefault(ns, set()).add(module.path)
        elif framework == 'python': # Converts absolute path → relative path → module name
            relative = Path(module.path).resolve().relative_to(Path(repository).resolve())
            name = relative.with_suffix('').as_posix().replace('/', '.')
            dct.setdefault(name, set()).add(module.path)
        else:
            raise ValueError(f"Check the execution parameters, the {framework} framework is not currently supported")
        
    return dct

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE