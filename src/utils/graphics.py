# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from pathlib import Path
from graphviz import Digraph
from typing import List, Dict, Set
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
# Get listed here!
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['map_to_graph']


def map_to_graph(dep_map: Dict[str, Set[str]], format: str) -> Digraph:
    """
    
    """
    dot = Digraph(format=format)
    dot.attr(
        ranksep='1',
        nodesep='1.2'
    )

    all_path = _get_all_path(dep_map)

    id_map = _build_id_map(all_path)

    groups: Dict[str, List[str]] = {}
    for path in all_path:
        name = Path(path).parent.name or 'root'
        groups.setdefault(name, []).append(path)

    for name, paths in groups.items():
        sub = Digraph(name=f'cluster_{name.lower()}')
        sub.attr(
            label=name, 
            style='rounded', 
            fontsize='10', 
            color='lightgrey'
        )

        for path in paths:
            sub.node(
                id_map[path], 
                _short_label(path), 
                fontsize='10', 
                color='lightgrey'
            )

        dot.subgraph(sub)

    for src, targets in dep_map.items():
        src_name = Path(src).parent.name or 'root'
        src_id = id_map[src]

        for dst in targets:
            dst_name = Path(dst).parent.name or 'root'
            dst_id = id_map[dst]

            if src_name == dst_name:
                dot.edge(src_id, dst_id)

    return dot

def _get_all_path(dep_map: Dict[str, Set[str]]) -> List[str]:
    """
    
    """
    all_path = list(dep_map.keys())

    for path in dep_map.values():
        all_path.extend(list(path))

    return sorted(set(all_path))

def _build_id_map(all_path: List[str]) -> Dict[str, str]:
    """
    
    """
    return {path: f'm{idx}' for idx, path in enumerate(all_path)}

def _short_label(path: str) -> str:
    """

    """
    return Path(path).stem

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE