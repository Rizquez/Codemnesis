# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
import re
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, List, Dict, Set
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.utils.maps import dependencies_map
from src.utils.graphics import map_to_graph

if TYPE_CHECKING:
    from src.models import ModuleInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['generate_graph']

FILE = 'Graphic'

def generate_graph( modules: List['ModuleInfo'], output: str, repository: str, *, format: str = 'svg') -> str:
    """
    
    """
    dep_map: Dict[str, Set] = _build_map(modules, repository)

    graph = map_to_graph(repository, dep_map, format)

    out = Path(output) / f'{FILE}.{format}'

    graph.render(out.with_suffix(''), cleanup=True)

    return out

def _build_map(modules: List['ModuleInfo'], repository: str) -> object:
    """

    """
    return dependencies_map(modules, _get_paths(modules, repository))

def _get_paths(modules: List['ModuleInfo'], repository: str) -> Dict[str, str]:
    """

    """
    dct = {}

    root = Path(repository).resolve()
    print(root)
    for module in modules:
        relative = Path(module.path).resolve().relative_to(root)
        print(relative)
        name = relative.with_suffix('').as_posix().replace('/', '.')
        dct[name] = module.path
    
    return dct

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE