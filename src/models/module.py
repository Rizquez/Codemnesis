# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from typing import List, Optional
from dataclasses import dataclass, field
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.models.entities import ClassInfo, FunctionInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['ModuleMetrics', 'ModuleInfo']

@dataclass
class ModuleMetrics:
    """
    It contains basic metrics extracted from a source module.

    Attributes:
        loc (int):
            Total number of lines in the file, including comments, blank lines, and code.
        sloc (int):
            Number of meaningful lines in the file, excluding comments and blank lines.
        n_classes (int):
            Total number of classes detected in the module.
        n_functions (int):
            Number of functions defined at the module level.
        n_methods (int):
            Total number of methods defined within all classes of the module.
    """
    loc: int
    sloc: int
    n_classes: int
    n_functions: int
    n_methods: int

@dataclass
class ModuleInfo:
    """
    Represents the analyzed structure of a source code file or module.

    Attributes:
        path (str):
            Full path to the file that was analyzed.
        doc (str, optional):
            Docstring of the module, if defined at the beginning of the file.
        functions (List[FunctionInfo]):
            List of functions defined at the module level.
        classes (List[ClassInfo]):
            List of classes found in the module, including their internal methods.
        imports(List[str]):
            List of imports on the module.
        metrics (ModuleMetrics, optional):
            Metrics associated with the module.
    """
    path: str
    doc: Optional[str]
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    imports: List[str] = field(default_factory=list)
    metrics: Optional[ModuleMetrics] = None

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE