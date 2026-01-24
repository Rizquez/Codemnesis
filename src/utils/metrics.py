# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import List, TYPE_CHECKING
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.tools.nums import percentage
from src.models import ModuleMetrics, RepositoryMetrics

if TYPE_CHECKING:
    from src.models import ClassInfo, FunctionInfo, ModuleInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

def module_metrics(src: str, classes: List[ClassInfo], funcs: List[FunctionInfo]) -> ModuleMetrics:
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

def repository_metrics(modules: List[ModuleInfo], repository: str) -> RepositoryMetrics:
    """
    Calculates aggregate metrics for a repository from a list of modules that have already been analyzed.

    It traverses the modules (sorted by their path), accumulates code size metrics (LOC/SLOC), and counts 
    design/documentation elements in classes.

    In addition, it builds two structures per module:
        - modules_overview: general summary per file (lines, number of classes/methods/functions, and attributes).
        - module_stats: documentation-oriented summary per file (SLOC, counts, and % implied via totals).

    Args:
        modules (List[ModuleInfo]):
            List of analyzed modules, each ModuleInfo must expose:
                - path: module file path.
                - metrics: object with metrics.
                - classes: collection of module classes; each class with doc, methods, and attributes.
        repository (str):
            Root path of the repository. Used to calculate a relative file name, taking the name from the relative path.

    Returns:
        RepositoryMetrics:
            Object with aggregated metrics from the repository.
    """
    loc = 0
    sloc = 0

    classes = 0
    documented_classes = 0

    methods = 0
    documented_methods = 0

    attributes = 0
    documented_attributes = 0

    module_stats = []
    modules_overview = []
    
    for module in sorted(modules, key=lambda module: module.path):
        metrics = module.metrics

        if not metrics:
            continue

        module_name = Path(module.path).resolve().relative_to(Path(repository).resolve()).name

        loc += metrics.loc or 0
        sloc += metrics.sloc or 0

        module_attributes = 0

        module_classes = 0
        module_documented_classes = 0

        module_methods = 0
        module_documented_methods = 0

        module_attributes = 0
        module_documented_attributes = 0

        for cls in module.classes:
            classes += 1
            module_classes += 1
            module_attributes += len(cls.attributes)

            if cls.doc and cls.doc.strip():
                documented_classes += 1
                module_documented_classes += 1

            for meth in cls.methods:
                methods += 1
                module_methods += 1

                if meth.doc and meth.doc.strip():
                    documented_methods += 1
                    module_documented_methods += 1

            for attr in cls.attributes:
                attributes += 1
                module_attributes += 1

                if attr.doc and attr.doc.strip():
                    documented_attributes += 1
                    module_documented_attributes += 1

        modules_overview.append({
            'name': module_name,
            'loc': metrics.loc,
            'sloc': metrics.sloc,
            'n_classes': metrics.n_classes,
            'n_methods': metrics.n_methods,
            'n_functions': metrics.n_functions,
            'n_attributes': module_attributes
        })

        module_stats.append({
            'name': module_name,
            'sloc': metrics.sloc or 0,
            'n_classes': metrics.n_classes,
            'n_methods': metrics.n_methods,
            'n_functions': metrics.n_functions,
            'total_items': module_classes + module_methods + module_attributes,
            'documented_items': module_documented_classes + module_documented_methods + module_documented_attributes
        })

    return RepositoryMetrics(
        loc=loc,
        sloc=sloc,
        module_stats=module_stats,
        modules_overview=modules_overview,
        class_percent=percentage(documented_classes, classes),
        method_percent=percentage(documented_methods, methods),
        attribute_percent=percentage(documented_attributes, attributes)
    )

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE