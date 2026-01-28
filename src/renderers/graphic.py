# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Set, TYPE_CHECKING
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.utils.maps import dependencies_map
from src.renderers.builders.diagram import dependency_diagram

if TYPE_CHECKING:
    from src.models import ModuleInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['render_graphic']

FILE = 'Dependency-Diagram'

def render_graphic(
    modules: List[ModuleInfo], 
    output: str, 
    repository: str, 
    framework: str, 
    *, 
    file_format: str = 'svg'
) -> Path:
    """
    Generates the dependency graph found between the analyzed modules.

    This method builds the internal dependency map of the code, invokes the generation of the corresponding graph, 
    and physically stores it in the user-defined path. The graph is generated according to the type of framework 
    evaluated, since each framework requires a different analysis of how the modules are structured.

    Args:
        modules (List[ModuleInfo]):
            List of `ModuleInfo` objects representing the analyzed modules in the repository.
        output (str):
            Path of the directory where the file will be stored.
        repository (str):
            Base path of the repository or project to be analyzed.
        framework (str):
            Name of the framework used, which must have a compatible mapping method.
        file_format (str, optional):
            Final format of the graph file.
    
    Returns:
        Path:
            Absolute path of the generated output file.
    """
    out = Path(output) / f'{FILE}.{file_format}'
    dep_map = dependencies_map(modules, repository, framework)
    graph = dependency_diagram(repository, dep_map, file_format)
    graph.render(out.with_suffix(''), cleanup=True)
    return out

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE