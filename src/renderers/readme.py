# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import List, TYPE_CHECKING
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.renderers.builders.markdown import generate_content

if TYPE_CHECKING:
    from src.models import ModuleInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['render_readme']

FILE = 'Documentation.md'

def render_readme(modules: List[ModuleInfo], repository: str, output: str) -> Path:
    """
    Write the generated README content to the file system.

    Args:
        modules (List[ModuleInfo]):
            List of `ModuleInfo` objects representing the analyzed modules in the repository.
        repository (str):
            Base path of the repository or project to be analyzed.
        output (str):
            Path of the directory where the file will be stored.

    Returns:
        Path:
            Full path of the generated README file.
    """
    path = Path(output)
    out = path / FILE
    text = generate_content(modules, repository)
    out.write_text(text, encoding='utf-8')
    return out
    
# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE