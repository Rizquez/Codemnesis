# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from typing import TYPE_CHECKING, List
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.models import ModuleMetrics

if TYPE_CHECKING:
    from src.models import ClassInfo, FunctionInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['module_metrics']

def module_metrics(src: str, classes: List['ClassInfo'], funcs: List['FunctionInfo']) -> ModuleMetrics:
    """
    Calculate basic module metrics from the source content and the previously analyzed structure.

    Args:
        src (str):
            Full content of the source file.
        classes (List[ClassInfo]):
            List of classes detected in the module.
        funcs (List[FunctionInfo]):
            List of functions defined at the module level.

    Returns:
        ModuleMetrics:
            Object containing all the metrics calculated for the analyzed file.
    """
    return ModuleMetrics(
        loc=len(src.splitlines()),
        sloc=sum(1 for line in src.splitlines() if line.strip() and not line.strip().startswith('#')),
        n_classes=len(classes),
        n_functions=len(funcs),
        n_methods=sum(len(cls.methods) for cls in classes)
    )

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE